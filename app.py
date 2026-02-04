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
    st.session_state.rotation = 1

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
# 選手番号入力
# ------------------
st.subheader("サーバー選択")
players = st.multiselect(
    "出場選手の番号",
    options=[i for i in range(1, 31)]
)

server = st.selectbox("サーブを打った選手番号", players)

# ------------------
# 結果入力
# ------------------
st.subheader("サーブ結果")

result = st.radio(
    "結果を選択",
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
if st.button("記録"):
    if point == "自チーム得点":
        st.session_state.team_score += 1
        if st.session_state.team_score > 1:
            st.session_state.rotation = st.session_state.rotation % 6 + 1
    else:
        st.session_state.opp_score += 1

ace = 1 if result == "サービスエース" else 0
effect = 1 if result == "Cパス" else 0
miss = 1 if result == "サーブミス" else 0

st.session_state.log.append({
    "date": match_date,
    "match": match_name,
    "set": st.session_state.set_no,
    "rally": st.session_state.rally_no,
    "team_score": st.session_state.team_score,
    "opp_score": st.session_state.opp_score,
    "rotation": st.session_state.rotation,
    "server": server,
    "result": result,
    "ace": ace,
    "effect": effect,
    "miss": miss
})

    st.session_state.rally_no += 1

# ------------------
# Undo
# ------------------
if st.button("Undo（1つ戻す）"):
    if len(st.session_state.log) > 0:
        st.session_state.log.pop()
        st.session_state.rally_no -= 1

# ------------------
# セット終了判定
# ------------------
if st.session_state.team_score >= max_score or st.session_state.opp_score >= max_score:
    st.success("セット終了")
    if st.button("次のセットへ"):
        st.session_state.set_no += 1
        st.session_state.team_score = 0
        st.session_state.opp_score = 0
        st.session_state.rotation = 1
        st.session_state.rally_no = 1

st.divider()

# ------------------
# データ表示
# ------------------
st.subheader("記録データ")

df = pd.DataFrame(st.session_state.log)
st.dataframe(df, use_container_width=True)

# ------------------
# サーブ効果率（関大式）
# ------------------
st.subheader("📊 サーブ効果率（関大式）")

if not df.empty:
    summary = (
        df.groupby(["server", "set"])
        .agg(
            打数=("result", "count"),
            ACE=("ace", "sum"),
            効果=("effect", "sum"),
            失点=("miss", "sum")
        )
        .reset_index()
    )

    summary["サーブ効果率（%）"] = (
        (summary["ACE"] * 100
         + summary["効果"] * 25
         - summary["失点"] * 25)
        / summary["打数"]
    ).round(1)

    st.dataframe(summary, use_container_width=True)

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
