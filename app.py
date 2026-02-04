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
    max_score = st.number_input("セット得点（15 / 25 など）", value=25)

st.divider()

# ------------------
# サーブ順入力
# ------------------
st.subheader("🔄 サーブ順入力（セット開始前）")

colA, colB = st.columns(2)

with colA:
    my_rotation = st.text_input(
        "自チーム サーブ順（例: 3,7,12,1,5,9）"
    )

with colB:
    opp_rotation = st.text_input(
        "相手チーム サーブ順（例: 8,4,6,10,2,11）"
    )

if st.button("サーブ順を確定"):
    try:
        st.session_state.my_servers = [int(x) for x in my_rotation.split(",")]
        st.session_state.opp_servers = [int(x) for x in opp_rotation.split(",")]
        st.session_state.rotation = 0
        st.session_state.serve_team = "自チーム"
        st.success("サーブ順を設定しました")
    except:
        st.error("サーブ順はカンマ区切りの数字で入力してください")

st.divider()

# ------------------
# 現在の状況表示
# ------------------
st.subheader("📍 現在の状況")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("自チーム得点", st.session_state.team_score)

with col2:
    st.metric("相手チーム得点", st.session_state.opp_score)

with col3:
    if st.session_state.serve_team == "自チーム" and st.session_state.my_servers:
        current_server = st.session_state.my_servers[
            st.session_state.rotation % 6
        ]
        server_label = f"自チーム {current_server}番"
    elif st.session_state.opp_servers:
        current_server = st.session_state.opp_servers[
            st.session_state.rotation % 6
        ]
        server_label = f"相手チーム {current_server}番"
    else:
        current_server = None
        server_label = "未設定"

    st.metric("現在のサーバー", server_label)

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
    if current_server is None:
        st.warning("サーブ順を先に確定してください")
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

st.rerun()

# ------------------
# Undo
# ------------------
if st.button("Undo（1つ戻す）"):
    if len(st.session_state.log) > 0:
        st.session_state.log.pop()
        st.session_state.rally_no -= 1
        st.divider()
# ------------------
# データ表示
# ------------------
st.subheader("📋 記録データ")

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
