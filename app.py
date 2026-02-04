import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# ------------------
# 初期設定
# ------------------
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

if "my_servers" not in st.session_state:
    st.session_state.my_servers = []

if "opp_servers" not in st.session_state:
    st.session_state.opp_servers = []

if "need_rerun" not in st.session_state:
    st.session_state.need_rerun = False

# ------------------
# タイトル・試合情報
# ------------------
st.title("🏐 サーブ効果率記録アプリ")

col1, col2, col3 = st.columns(3)
with col1:
    match_date = st.date_input("試合日", datetime.today())
with col2:
    match_name = st.text_input("試合名")
with col3:
    max_score = st.number_input("セット得点（15/25など）", value=25)

st.divider()

# ------------------
# サーブ順入力
# ------------------
st.subheader("🔁 サーブ順入力（左→右）")

colA, colB = st.columns(2)
with colA:
    st.session_state.my_servers = st.multiselect(
        "自チーム サーブ順（6人）",
        options=list(range(1, 31)),
        default=st.session_state.my_servers
    )
with colB:
    st.session_state.opp_servers = st.multiselect(
        "相手チーム サーブ順（6人）",
        options=list(range(1, 31)),
        default=st.session_state.opp_servers
    )

def get_current_server():
    if st.session_state.serve_team == "自チーム" and len(st.session_state.my_servers) == 6:
        return st.session_state.my_servers[st.session_state.rotation % 6]
    if st.session_state.serve_team == "相手" and len(st.session_state.opp_servers) == 6:
        return st.session_state.opp_servers[st.session_state.rotation % 6]
    return None

current_server = get_current_server()

st.divider()

# ------------------
# 現在状況表示
# ------------------
st.subheader("📊 現在の状況")

colS1, colS2, colS3 = st.columns(3)
with colS1:
    st.metric("自チーム得点", st.session_state.team_score)
with colS2:
    st.metric("相手得点", st.session_state.opp_score)
with colS3:
    if current_server is not None:
        st.metric(
            "現在のサーバー",
            f"{st.session_state.serve_team}：#{current_server}"
        )
    else:
        st.warning("サーブ順が未完成です")

st.divider()

# ------------------
# 結果入力
# ------------------
st.subheader("📝 サーブ結果入力")

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

# ------------------
# 記録ボタン
# ------------------
if st.button("▶ 記録"):
    if current_server is None:
        st.warning("サーブ順を6人分入力してください")
        st.stop()

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

    st.session_state.need_rerun = True

# ------------------
# セット終了判定
# ------------------
if st.session_state.team_score >= max_score or st.session_state.opp_score >= max_score:
    st.success("🏁 セット終了")
    if st.button("次のセットへ"):
        st.session_state.set_no += 1
        st.session_state.team_score = 0
        st.session_state.opp_score = 0
        st.session_state.rotation = 0
        st.session_state.rally_no = 1
        st.session_state.serve_team = "自チーム"
        st.session_state.need_rerun = True

st.divider()

# ------------------
# 記録表示
# ------------------
st.subheader("📋 記録一覧")
df = pd.DataFrame(st.session_state.log)
st.dataframe(df, use_container_width=True)

# ------------------
# CSVエクスポート
# ------------------
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVダウンロード",
        csv,
        file_name="serve_log.csv",
        mime="text/csv"
    )

# ------------------
# rerun（1回だけ）
# ------------------
if st.session_state.need_rerun:
    st.session_state.need_rerun = False
    st.rerun()
