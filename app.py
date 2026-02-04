import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# =====================
# 初期化
# =====================
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

if "need_rotation" not in st.session_state:
    st.session_state.need_rotation = False

if "serve_order" not in st.session_state:
    st.session_state.serve_order = []

if "pending_result" not in st.session_state:
    st.session_state.pending_result = None

if "pending_point" not in st.session_state:
    st.session_state.pending_point = None

# =====================
# タイトル・試合情報
# =====================
st.title("🏐 サーブ効果率記録アプリ")

col1, col2, col3 = st.columns(3)
with col1:
    match_date = st.date_input("試合日", datetime.today())
with col2:
    match_name = st.text_input("試合名")
with col3:
    max_score = st.number_input("セット得点（15 / 25 など）", value=25)

st.divider()

# =====================
# サーブ順入力
# =====================
st.subheader("サーブ順（6人）")

serve_order = st.multiselect(
    "サーブ順を1番目→6番目の順で選択",
    options=[i for i in range(1, 31)],
    max_selections=6
)

if len(serve_order) == 6:
    st.session_state.serve_order = serve_order
    st.success("サーブ順が確定しました")

if len(st.session_state.serve_order) == 6:
    current_server = st.session_state.serve_order[
        (st.session_state.rotation - 1) % 6
    ]
else:
    current_server = None

# =====================
# 現在の状況表示
# =====================
st.subheader("現在の状況")

colA, colB, colC = st.columns(3)
with colA:
    st.metric("自チーム得点", st.session_state.team_score)
with colB:
    st.metric("相手得点", st.session_state.opp_score)
with colC:
    st.metric(
        "現在のサーバー",
        f"自チーム #{current_server}" if current_server else "-"
    )

st.divider()

# =====================
# サーブ結果入力
# =====================
st.subheader("サーブ結果入力")

st.session_state.pending_result = st.radio(
    "サーブの効果",
    ["サービスエース", "Aパス", "Bパス", "Cパス", "サーブミス"]
)

st.session_state.pending_point = st.radio(
    "得点",
    ["自チーム得点", "相手チーム得点"],
    horizontal=True
)

# =====================
# 記録ボタン（1回で確定）
# =====================
if st.button("記録"):
    result = st.session_state.pending_result
    point = st.session_state.pending_point

    # 得点処理
    if point == "自チーム得点":
        st.session_state.team_score += 1
        if st.session_state.need_rotation:
            st.session_state.rotation = st.session_state.rotation % 6 + 1
            st.session_state.need_rotation = False
    else:
        st.session_state.opp_score += 1
        st.session_state.need_rotation = True

    # ログ保存
    st.session_state.log.append({
        "date": match_date,
        "match": match_name,
        "set": st.session_state.set_no,
        "rally": st.session_state.rally_no,
        "team_score": st.session_state.team_score,
        "opp_score": st.session_state.opp_score,
        "rotation": st.session_state.rotation,
        "server": current_server,
        "result": result
    })

    st.session_state.rally_no += 1

# =====================
# Undo
# =====================
if st.button("Undo（1つ戻す）"):
    if st.session_state.log:
        st.session_state.log.pop()
        st.session_state.rally_no -= 1

# =====================
# セット終了
# =====================
if (
    st.session_state.team_score >= max_score
    or st.session_state.opp_score >= max_score
):
    st.success("セット終了")
    if st.button("次のセットへ"):
        st.session_state.set_no += 1
        st.session_state.team_score = 0
        st.session_state.opp_score = 0
        st.session_state.rotation = 1
        st.session_state.rally_no = 1
        st.session_state.need_rotation = False

st.divider()

# =====================
# データ表示
# =====================
st.subheader("記録データ")

df = pd.DataFrame(st.session_state.log)
st.dataframe(df, use_container_width=True)

# =====================
# サーブ効果率
# =====================
if not df.empty:
    df["ace"] = (df["result"] == "サービスエース").astype(int)
    df["effect"] = (df["result"] == "Cパス").astype(int)
    df["miss"] = (df["result"] == "サーブミス").astype(int)

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

    st.subheader("サーブ効果率")
    st.dataframe(summary, use_container_width=True)

# =====================
# CSV出力
# =====================
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSVダウンロード",
        csv,
        file_name="serve_log.csv",
        mime="text/csv"
    )
