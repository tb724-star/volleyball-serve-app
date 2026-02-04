import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# ==================
# 初期化
# ==================
def init_state():
    defaults = {
        "log": [],
        "set_no": 1,
        "rally_no": 1,
        "team_score": 0,
        "opp_score": 0,
        "serving_team": "my",  # my / opp
        "my_rotate_idx": 0,
        "opp_rotate_idx": 0,
        "my_servers": [],
        "opp_servers": [],
        "tmp_my_servers": [],
        "tmp_opp_servers": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

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
# サーブ順入力（form）
# ==================
st.subheader("🔁 サーブ順入力")

with st.form("serve_order_form"):
    colA, colB = st.columns(2)

    with colA:
        tmp_my = st.multiselect(
            "自チーム（6人）",
            options=list(range(1, 31)),
            default=st.session_state.tmp_my_servers
        )
    with colB:
        tmp_opp = st.multiselect(
            "相手チーム（6人）",
            options=list(range(1, 31)),
            default=st.session_state.tmp_opp_servers
        )

    submitted = st.form_submit_button("サーブ順を確定")

    if submitted:
        if len(tmp_my) != 6 or len(tmp_opp) != 6:
            st.error("両チーム6人ずつ選んでください")
        else:
            st.session_state.my_servers = tmp_my
            st.session_state.opp_servers = tmp_opp
            st.session_state.tmp_my_servers = tmp_my
            st.session_state.tmp_opp_servers = tmp_opp
            st.success("サーブ順を確定しました")

# ==================
# 現在のサーバー表示
# ==================
st.divider()

if st.session_state.my_servers and st.session_state.opp_servers:
    if st.session_state.serving_team == "my":
        current_server = st.session_state.my_servers[st.session_state.my_rotate_idx]
        st.info(f"🏐 自チーム サーバー：#{current_server}")
    else:
        current_server = st.session_state.opp_servers[st.session_state.opp_rotate_idx]
        st.warning(f"🏐 相手チーム サーバー：#{current_server}")

    st.write(
        f"🔢 得点　自チーム {st.session_state.team_score} − "
        f"{st.session_state.opp_score} 相手"
    )

# ==================
# サーブ結果入力 & 記録（form）
# ==================
st.subheader("サーブ結果")

with st.form("record_form"):

    result = st.radio(
        "効果",
        ["サービスエース", "Cパス", "Bパス", "Aパス", "サーブミス"],
        horizontal=True
    )

    point = st.radio(
        "得点",
        ["自チーム得点", "相手得点"],
        horizontal=True
    )

    submitted = st.form_submit_button("記録")

    if submitted:

        prev_serving = st.session_state.serving_team

        # 得点処理
        if point == "自チーム得点":
            st.session_state.team_score += 1
            scorer = "my"
        else:
            st.session_state.opp_score += 1
            scorer = "opp"

        # サーブ権・ローテ処理
        if scorer != prev_serving:
            st.session_state.serving_team = scorer

            if scorer == "my":
                st.session_state.my_rotate_idx = (st.session_state.my_rotate_idx + 1) % 6
            else:
                st.session_state.opp_rotate_idx = (st.session_state.opp_rotate_idx + 1) % 6

        # ログ保存
        st.session_state.log.append({
            "date": match_date,
            "match": match_name,
            "set": st.session_state.set_no,
            "rally": st.session_state.rally_no,
            "serving_team": prev_serving,
            "server": current_server,
            "result": result,
            "point": point,
            "team_score": st.session_state.team_score,
            "opp_score": st.session_state.opp_score,
        })

        st.session_state.rally_no += 1

# ==================
# 記録処理（核心）
# ==================
if st.button("記録"):

    prev_serving = st.session_state.serving_team

    # 得点処理
    if point == "自チーム得点":
        st.session_state.team_score += 1
        scorer = "my"
    else:
        st.session_state.opp_score += 1
        scorer = "opp"

    # サーブ権・ローテ処理
    if scorer != prev_serving:
        # サーブ権が移動
        st.session_state.serving_team = scorer

        if scorer == "my":
            st.session_state.my_rotate_idx = (st.session_state.my_rotate_idx + 1) % 6
        else:
            st.session_state.opp_rotate_idx = (st.session_state.opp_rotate_idx + 1) % 6

    # ログ保存
    st.session_state.log.append({
        "date": match_date,
        "match": match_name,
        "set": st.session_state.set_no,
        "rally": st.session_state.rally_no,
        "serving_team": prev_serving,
        "server": current_server,
        "result": result,
        "point": point,
        "team_score": st.session_state.team_score,
        "opp_score": st.session_state.opp_score,
    })

    st.session_state.rally_no += 1


# ==================
# データ表示
# ==================
st.divider()
st.subheader("記録一覧")

df = pd.DataFrame(st.session_state.log)
st.dataframe(df, use_container_width=True)

# ==================
# CSV
# ==================
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVダウンロード",
        csv,
        file_name="serve_log.csv",
        mime="text/csv"
    )
