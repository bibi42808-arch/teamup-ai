import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #eef3ff;
            --bg-soft: #f7f9ff;
            --card: rgba(255,255,255,0.92);
            --card-strong: #ffffff;
            --navy: #0f172a;
            --navy-2: #1e293b;
            --violet: #5b5ce6;
            --violet-2: #7c4dff;
            --teal: #14b8a6;
            --muted: #5b6785;
            --line: rgba(148, 163, 184, 0.28);
            --success: #0f9f6e;
            --warning: #f59e0b;
            --danger: #e11d48;
            --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background:
                radial-gradient(circle at top left, rgba(91, 92, 230, 0.12), transparent 28%),
                radial-gradient(circle at bottom right, rgba(20, 184, 166, 0.12), transparent 22%),
                var(--bg-soft);
            color: var(--navy);
        }

        .stApp {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
            border-right: 1px solid rgba(148,163,184,0.17);
        }

        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stButton button {
            color: #e2e8f0 !important;
        }

        .stRadio > div {
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            padding: 0.8rem 0.6rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        .card {
            background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(247,249,255,0.96) 100%);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1.3rem 1.4rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 22px 46px rgba(15, 23, 42, 0.12);
        }

        .hero-box {
            background: linear-gradient(120deg, #101b36 0%, #18284d 40%, #2a2259 100%);
            color: white;
            border-radius: 28px;
            padding: 2rem 2rem 1.5rem 2rem;
            box-shadow: 0 22px 48px rgba(21, 27, 52, 0.18);
            border: 1px solid rgba(255,255,255,0.06);
            margin-bottom: 1.5rem;
        }

        .hero-box h1 {
            color: white !important;
            font-size: 3rem !important;
            line-height: 1.1;
            letter-spacing: -0.05em;
            font-weight: 800;
            margin-bottom: 0.65rem;
        }

        .hero-box p {
            color: rgba(255,255,255,0.8) !important;
            font-size: 1.08rem;
            max-width: 700px;
        }

        .hero-action-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .stButton > button {
            border-radius: 12px;
            border: none;
            padding: 0.7rem 1.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--violet) 0%, var(--violet-2) 100%);
            color: #fff;
            box-shadow: 0 12px 24px rgba(91, 92, 230, 0.22);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #4f52d7 0%, #6a4ef2 100%);
            color: #fff;
        }

        .stButton button[kind="secondary"] {
            background: transparent !important;
            color: var(--navy) !important;
            border: 1px solid rgba(148,163,184,0.38) !important;
            box-shadow: none;
        }

        .feature-pill {
            color: var(--navy) !important;
            font-weight: 700;
            border: 1px solid rgba(91,92,230,0.12);
            background: rgba(91,92,230,0.06);
            border-radius: 999px;
            padding: 0.4rem 0.8rem;
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .stat-box {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(241,245,255,0.98));
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1.1rem 1rem;
            box-shadow: var(--shadow);
            text-align: center;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.4rem;
            color: var(--navy);
        }

        h1, h2, h3, h4, h5 {
            color: var(--navy) !important;
            letter-spacing: -0.03em;
        }

        p, li, div {
            color: var(--navy-2);
        }

        input, textarea, select {
            border-radius: 12px !important;
            border: 1px solid rgba(148, 163, 184, 0.42) !important;
            box-shadow: none !important;
        }

        .stTabs [role="tablist"] {
            gap: 0.5rem;
        }

        .stTabs [role="tab"] {
            border-radius: 12px 12px 0 0;
            padding: 0.7rem 1rem;
            font-weight: 600;
        }

        .stTabs [role="tab"][aria-selected="true"] {
            background: rgba(91, 92, 230, 0.09);
            border-bottom: 2px solid var(--violet);
        }

        .stSuccess, .stWarning, .stInfo {
            border-radius: 14px;
            border: 1px solid rgba(148,163,184,0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
