import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# ==================
# 初期設定
# ==================
if "log" not in st.session_state:
    st.session_state.log = []

if "set_no" not in st.session_state:
    st.session_state.set_no = 1

if "rally_no" not in st.session_state:
    st.session_state.rally_no = 1

if "team_score" not in st.session_state:
    st.session_state.team_score = 0

if "opp_score" not in st.session_state:
    st.session_state.opp_score = 0

if "rotation" not in st.session_state:
    st.session_state.rotation = 0  # 0〜5

if "serve_team" not in st.session_state:
    st.session_state.serve_team = "自チーム"

# 確定済みサーブ順
if "my_servers" not in st.session_state:
    st.session_state.my_servers = []

if "opp_servers" not in st.session_state:
    st.session_state.opp_servers = []

# 入力中サーブ順（ここが重要）
if "tmp_my_servers" not in st.session_state:
    st.session_state.tmp_my_servers = []

if "tmp_opp_servers" not in st.session_state:
    st.session_state.tmp_opp_servers = []

# ==================
# 関数
# ==================
def get_current_server():
    if st.session_state.serve_team == "自チーム":
        if len(st.session_state.my_servers) == 6:
            return st.session_state.my_servers[st.session_state.rotation % 6]
    else:
        if len(st.session_state.opp_servers) == 6:
            return st.session_state.opp_servers[st.session_state.rotation % 6]
    return None

# ==================
# タイトル・試合情報
# ==================
st.title("🏐 サーブ効果率記録アプリ")

col1, col2, col3 = st.columns(3)
with col1:
    match_date = st.date_input("試合日", datetime.today())
with col2:
    match_name = st.text_input("試合名")
with col3:
    max_score = st.number_input("セット得点（15 / 25など）", value=25)

st.divider()



# ==================
# 現在状況表示
# ==================
st.subheader("📊 現在の状況")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("自チーム得点", st.session_state.team_score)
with c2:
    st.metric("相手得点", st.session_state.opp_score)
with c3:
    server_now = get_current_server()
    if server_now is not None:
        st.metric("現在のサーバー", f"{st.session_state.serve_team}：#{server_now}")
    else:
        st.warning("サーブ順が未確定です")

st.divider()
# ==================
# サーブ順入力（formで固定）
# ==================
st.subheader("🔁 サーブ順入力（6人選んで確定）")

with st.form("serve_order_form"):

    colA, colB = st.columns(2)

    with colA:
        tmp_my_servers = st.multiselect(
            "自チーム サーブ順（左→右）",
            options=list(range(1, 31)),
            default=st.session_state.tmp_my_servers
        )

    with colB:
        tmp_opp_servers = st.multiselect(
            "相手チーム サーブ順（左→右）",
            options=list(range(1, 31)),
            default=st.session_state.tmp_opp_servers
        )

    submit = st.form_submit_button("✅ サーブ順を確定")

    if submit:
        if len(tmp_my_servers) != 6 or len(tmp_opp_servers) != 6:
            st.error("自チーム・相手チームともに6人選択してください")
        else:
            st.session_state.my_servers = tmp_my_servers.copy()
            st.session_state.opp_servers = tmp_opp_servers.copy()
            st.session_state.tmp_my_servers = tmp_my_servers.copy()
            st.session_state.tmp_opp_servers = tmp_opp_servers.copy()
            st.success("サーブ順を確定しました")
# ==================
# 結果入力
# ==================
st.subheader("📝 サーブ結果")

result = st.radio(
    "結果",
    ["サービスエース", "Cパス", "Bパス", "Aパス", "サーブミス"],
    horizontal=True
)

point = st.radio(
    "得点",
    ["自チーム得点", "相手得点"],
    horizontal=True
)

# ==================
# 記録処理
# ==================
if st.button("▶ 記録"):
    current_server = get_current_server()

    if current_server is None:
        st.warning("サーブ順を先に確定してください")
    else:
        ace = 1 if result == "サービスエース" else 0
        effect = 1 if result == "Cパス" else 0
        miss = 1 if result == "サーブミス" else 0

        st.session_state.log.append({
            "date": match_date,
            "match": match_name,
            "set": st.session_state.set_no,
            "rally": st.session_state.rally_no,
            "serve_team": st.session_state.serve_team,
            "server": current_server,
            "rotation": st.session_state.rotation + 1,
            "result": result,
            "ace": ace,
            "effect": effect,
            "miss": miss,
            "team_score": st.session_state.team_score,
            "opp_score": st.session_state.opp_score
        })

        if point == "自チーム得点":
            st.session_state.team_score += 1
            st.session_state.serve_team = "自チーム"
        else:
            st.session_state.opp_score += 1
            st.session_state.serve_team = "相手"

        st.session_state.rotation += 1
        st.session_state.rally_no += 1

# ==================
# セット終了
# ==================
if st.session_state.team_score >= max_score or st.session_state.opp_score >= max_score:
    st.success("🏁 セット終了")
    if st.button("次のセットへ"):
        st.session_state.set_no += 1
        st.session_state.team_score = 0
        st.session_state.opp_score = 0
        st.session_state.rotation = 0
        st.session_state.rally_no = 1
        st.session_state.serve_team = "自チーム"

st.divider()

# ==================
# 記録表示
# ==================
st.subheader("📋 記録一覧")

df = pd.DataFrame(st.session_state.log)
st.dataframe(df, use_container_width=True)

# ==================
# CSVエクスポート
# ==================
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVダウンロード",
        csv,
        file_name="serve_log.csv",
        mime="text/csv"
    )
