
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import openai

st.set_page_config(page_title="자산 전략 대시보드", layout="wide")
st.title("📊 포트폴리오 자산 전략 대시보드")

openai.api_key = st.secrets["OPENAI_API_KEY"]

def format_number(n):
    return f"{int(n):,}"

# 초기 세션 상태
if "assets" not in st.session_state:
    st.session_state.assets = [
        {"자산 종류": "현금", "금액": 50000000},
        {"자산 종류": "예적금", "금액": 20000000},
        {"자산 종류": "주식", "금액": 10000000},
        {"자산 종류": "부동산", "금액": 100000000},
        {"자산 종류": "기타", "금액": 3000000},
    ]

if "plans" not in st.session_state:
    st.session_state.plans = [
        {"연도": 2024, "목표": "부동산 매수", "예산": 130000000},
        {"연도": 2025, "목표": "ETF 확대", "예산": 10000000},
    ]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 연도별 목표 및 전략",
    "📥 자산 입력",
    "📋 자산 요약",
    "📈 도넛 차트",
    "🧠 GPT 분석"
])

with tab1:
    st.subheader("📅 연도별 목표 및 전략")
    plan_df = pd.DataFrame(st.session_state.plans)
    edited_plan_df = st.data_editor(plan_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 전략 저장"):
        st.session_state.plans = edited_plan_df.to_dict("records")
        st.success("📌 전략 저장 완료!")

    st.markdown("### 🎯 전략 요약 보기")
    if st.session_state.plans:
        summary = pd.DataFrame(st.session_state.plans)
        summary["예산"] = summary["예산"].map(lambda x: f"{x:,} 원")
        st.table(summary)

    st.markdown("### 🔁 시나리오 시뮬레이션")
    growth = st.slider("자산 연간 성장률 (%)", 0, 50, 8)
    years = [p["연도"] for p in st.session_state.plans]
    base = sum([a["금액"] for a in st.session_state.assets])
    sim_data = [{"연도": y, "예상 자산": int(base * ((1 + growth / 100) ** i))} for i, y in enumerate(years)]
    sim_df = pd.DataFrame(sim_data)
    sim_df["예상 자산"] = sim_df["예상 자산"].map(lambda x: f"{x:,} 원")
    st.table(sim_df)

with tab2:
    st.subheader("📥 자산 입력 및 편집")
    df = pd.DataFrame(st.session_state.assets)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 자산 저장"):
        st.session_state.assets = edited_df.to_dict("records")
        st.success("✅ 저장 완료!")

with tab3:
    st.subheader("📋 자산 카드형 요약")
    total = sum([a["금액"] for a in st.session_state.assets])
    cols = st.columns(len(st.session_state.assets))
    for i, asset in enumerate(st.session_state.assets):
        with cols[i]:
            st.markdown(f"""
                <div style='background-color:#1c1c1c;padding:20px;border-radius:15px;text-align:center;color:white'>
                    <h4>{asset['자산 종류']}</h4>
                    <p style='font-size:24px;margin:0;'>{format_number(asset['금액'])} 원</p>
                    <p style='margin:0;color:#999'>({asset['금액'] / total * 100:.1f}%)</p>
                </div>
            """, unsafe_allow_html=True)
    st.markdown(f"### 💵 총 자산 합계: **{format_number(total)} 원**")

with tab4:
    st.subheader("📈 자산 비중 도넛 차트")
    labels = [row["자산 종류"] for row in st.session_state.assets]
    values = [row["금액"] for row in st.session_state.assets]
    colors = ['#A569BD', '#5DADE2', '#48C9B0', '#F4D03F', '#EC7063', '#58D68D']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        textinfo='label+percent',
        hoverinfo='label+percent+value',
        marker=dict(colors=colors, line=dict(color='#000000', width=1))
    )])
    fig.update_layout(
        template='plotly_dark',
        annotations=[dict(text=f'{format_number(total)}원', x=0.5, y=0.5, font_size=20, showarrow=False)],
        margin=dict(t=30, b=30, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("🧠 GPT 자산 분석 및 전략 추천")
    if "gpt_feedback" not in st.session_state:
        st.session_state.gpt_feedback = ""

    if st.button("💬 GPT 전략 요청"):
        try:
            msg = f"""자산 목록: {st.session_state.assets}\n목표 계획: {st.session_state.plans}\n이 사람에게 적절한 자산 전략을 요약해서 3가지 포인트로 정리해줘."""
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": msg}]
            )
            st.session_state.gpt_feedback = response["choices"][0]["message"]["content"]
        except Exception as e:
            st.session_state.gpt_feedback = f"❌ 오류 발생: {e}"

    st.text_area("GPT 전략 분석 결과", st.session_state.gpt_feedback, height=250)
