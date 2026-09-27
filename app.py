import json
import os
import time
import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = BASE_DIR / "assets" / "cyber_astra_logo.png"
ALERT_FILE = BASE_DIR / "data" / "alerts.json"
BENCHMARK_FILE = BASE_DIR / "data" / "benchmark_report.json"

# Local Ollama
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:14b"
)

EXPECTED_THREAT_COUNT = 6


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CYBER-ASTRA SOC",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_logo_base64():
    """Convert CYBER-ASTRA logo to base64."""

    if not LOGO_PATH.exists():
        return None

    try:
        with open(LOGO_PATH, "rb") as image_file:
            return base64.b64encode(
                image_file.read()
            ).decode("utf-8")

    except Exception:
        return None


def render_header_logo():
    """Render CYBER-ASTRA logo in dashboard header."""

    logo_base64 = get_logo_base64()

    if not logo_base64:

        st.markdown(
            """
            <div class="fallback-logo">
                🛡️ CYBER-ASTRA
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    st.markdown(
        f"""
        <div class="header-logo-wrapper">
            <img
                src="data:image/png;base64,{logo_base64}"
                class="header-logo"
                alt="CYBER-ASTRA"
            >
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_alerts():

    if not ALERT_FILE.exists():
        return pd.DataFrame()

    try:

        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        alerts = data.get(
            "alerts",
            []
        )

        if not alerts:
            return pd.DataFrame()

        return pd.DataFrame(
            alerts
        )

    except Exception as error:

        st.error(
            f"Unable to load alerts: {error}"
        )

        return pd.DataFrame()


def safe_float(
    value,
    default=0.0
):

    try:

        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# SESSION STATE
# ============================================================

if "landing_complete" not in st.session_state:

    st.session_state.landing_complete = False


# ============================================================
# CYBER-ASTRA CLICK-TO-ENTER LANDING SCREEN
# ============================================================

if not st.session_state.landing_complete:

    logo_base64 = get_logo_base64()

    # --------------------------------------------------------
    # FULL SCREEN LANDING CSS
    # --------------------------------------------------------

    if logo_base64:

        logo_background = (
            f"url(data:image/png;base64,{logo_base64})"
        )

    else:

        logo_background = "none"


    st.markdown(
        f"""
        <style>

        /* ====================================================
           HIDE NORMAL STREAMLIT UI
           ==================================================== */

        #MainMenu {{
            visibility: hidden;
        }}

        header {{
            visibility: hidden;
        }}

        footer {{
            visibility: hidden;
        }}

        [data-testid="stSidebar"] {{
            display: none;
        }}

        .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
        }}


        /* ====================================================
           FULL SCREEN ENTER BUTTON
           ==================================================== */

        div.stButton {{
            position: static;
        }}

        div.stButton > button {{
            position: fixed;

            inset: 0;

            width: 100vw;
            height: 100vh;

            margin: 0;
            padding: 0;

            border: none !important;
            border-radius: 0 !important;

            outline: none !important;

            cursor: pointer;

            z-index: 999999;

            color: transparent !important;

            background-color: #02050b;

            background-image:

                radial-gradient(
                    circle at center,
                    rgba(0,190,255,0.18),
                    transparent 28%
                ),

                radial-gradient(
                    circle at center,
                    rgba(0,80,180,0.12),
                    transparent 55%
                ),

                linear-gradient(
                    rgba(0,170,255,0.035) 1px,
                    transparent 1px
                ),

                linear-gradient(
                    90deg,
                    rgba(0,170,255,0.035) 1px,
                    transparent 1px
                ),

                {logo_background};

            background-size:

                auto,
                auto,
                55px 55px,
                55px 55px,
                280px auto;

            background-position:

                center,
                center,
                center,
                center,
                center 42%;

            background-repeat:

                no-repeat,
                no-repeat,
                repeat,
                repeat,
                no-repeat;

            box-shadow: none !important;

            transition:
                all 0.25s ease;
        }}


        div.stButton > button:hover {{

            background-color: #020812;

            background-image:

                radial-gradient(
                    circle at center,
                    rgba(0,210,255,0.24),
                    transparent 32%
                ),

                radial-gradient(
                    circle at center,
                    rgba(0,100,220,0.15),
                    transparent 58%
                ),

                linear-gradient(
                    rgba(0,190,255,0.05) 1px,
                    transparent 1px
                ),

                linear-gradient(
                    90deg,
                    rgba(0,190,255,0.05) 1px,
                    transparent 1px
                ),

                {logo_background};

            background-size:

                auto,
                auto,
                55px 55px,
                55px 55px,
                295px auto;

            background-position:

                center,
                center,
                center,
                center,
                center 42%;

            background-repeat:

                no-repeat,
                no-repeat,
                repeat,
                repeat,
                no-repeat;
        }}


        /* ====================================================
           TITLE
           ==================================================== */

        div.stButton > button::before {{

            content:
                "CYBER-ASTRA";

            position: absolute;

            top: 17%;

            left: 0;
            right: 0;

            text-align: center;

            color: #e8fbff;

            font-size: clamp(
                32px,
                5vw,
                62px
            );

            font-weight: 800;

            letter-spacing: 8px;

            text-shadow:

                0 0 10px
                rgba(0,210,255,0.65),

                0 0 30px
                rgba(0,140,255,0.40),

                0 0 60px
                rgba(0,100,255,0.20);
        }}


        /* ====================================================
           ENTER TEXT
           ==================================================== */

        div.stButton > button::after {{

            content:
                "CLICK ANYWHERE TO ENTER SOC";

            position: absolute;

            left: 0;
            right: 0;

            bottom: 15%;

            text-align: center;

            color: #7eeaff;

            font-size: 15px;

            font-weight: 700;

            letter-spacing: 4px;

            text-shadow:
                0 0 12px
                rgba(0,200,255,0.55);

            animation:
                landingPulse 2s
                ease-in-out
                infinite;
        }}


        /* ====================================================
           ANIMATION
           ==================================================== */

        @keyframes landingPulse {{

            0%, 100% {{
                opacity: 0.45;
            }}

            50% {{
                opacity: 1;
            }}
        }}


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 600px) {{

            div.stButton > button {{
                background-size:
                    auto,
                    auto,
                    40px 40px,
                    40px 40px,
                    210px auto;

                background-position:
                    center,
                    center,
                    center,
                    center,
                    center 42%;
            }}

            div.stButton > button::before {{

                top: 18%;

                font-size: 30px;

                letter-spacing: 5px;
            }}

            div.stButton > button::after {{

                bottom: 12%;

                font-size: 11px;

                letter-spacing: 2px;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # NATIVE STREAMLIT CLICK AREA
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # This is a real Streamlit button.
    #
    # The entire button covers the screen.
    #
    # Therefore the user can click anywhere.
    #
    # No JavaScript.
    # No HTML anchor.
    # No query parameters.
    # No timer.
    #
    # The landing page remains indefinitely until clicked.
    # --------------------------------------------------------

    if st.button(
        "ENTER CYBER-ASTRA SOC",
        key="landing_enter_button",
        use_container_width=True,
    ):

        st.session_state.landing_complete = True

        st.rerun()


    st.stop()


# ============================================================
# CUSTOM DASHBOARD CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at 50% -20%,
                rgba(0, 170, 255, 0.10),
                transparent 45%
            ),

            radial-gradient(
                circle at 90% 30%,
                rgba(0, 100, 255, 0.04),
                transparent 35%
            ),

            #050912;
    }


    .block-container {

        padding-top: 1.4rem;

        padding-bottom: 2rem;

        max-width: 1500px;
    }


    h1,
    h2,
    h3 {

        letter-spacing: 0.5px;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #070d18 0%,
                #050a13 100%
            );

        border-right:
            1px solid
            rgba(0, 200, 255, 0.15);
    }


    section[data-testid="stSidebar"] img {

        border-radius: 12px;

        margin-top: 4px;

        margin-bottom: 8px;
    }


    /* ======================================================
       HEADER LOGO
       ====================================================== */

    .header-logo-wrapper {

        width: 100%;

        display: flex;

        justify-content: center;

        align-items: center;

        padding-top: 2px;

        padding-bottom: 8px;
    }


    .header-logo {

        width: 360px;

        max-width: 65%;

        height: auto;

        object-fit: contain;

        filter:
            drop-shadow(
                0 0 14px
                rgba(0, 160, 255, 0.18)
            );
    }


    .fallback-logo {

        text-align: center;

        font-size: 2.2rem;

        font-weight: 800;

        padding-bottom: 10px;
    }


    /* ======================================================
       STATUS
       ====================================================== */

    .status-box {

        padding: 13px 18px;

        border-radius: 12px;

        background:
            linear-gradient(
                90deg,
                rgba(0, 170, 110, 0.10),
                rgba(0, 80, 90, 0.06)
            );

        border:
            1px solid
            rgba(0, 230, 150, 0.28);

        margin-bottom: 20px;

        box-shadow:
            0 0 18px
            rgba(0, 220, 150, 0.03);
    }


    /* ======================================================
       METRIC CARDS
       ====================================================== */

    div[data-testid="metric-container"] {

        background:
            linear-gradient(
                145deg,
                rgba(10, 20, 35, 0.95),
                rgba(7, 15, 28, 0.92)
            );

        border:
            1px solid
            rgba(0, 200, 255, 0.18);

        border-radius: 14px;

        padding: 14px;

        box-shadow:
            0 0 20px
            rgba(0, 140, 255, 0.05);
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {

        border-radius: 10px;

        border:
            1px solid
            rgba(0, 200, 255, 0.35);

        background:
            rgba(0, 120, 200, 0.12);

        font-weight: 600;

        transition:
            all 0.2s ease;
    }


    .stButton > button:hover {

        border-color:
            rgba(0, 220, 255, 0.8);

        background:
            rgba(0, 160, 240, 0.22);

        box-shadow:
            0 0 14px
            rgba(0, 180, 255, 0.10);
    }


    /* ======================================================
       ALERT CARDS
       ====================================================== */

    .alert-card {

        padding: 15px;

        border-radius: 12px;

        background:
            rgba(10, 20, 35, 0.8);

        border:
            1px solid
            rgba(0, 200, 255, 0.15);

        margin-bottom: 10px;
    }


    /* ======================================================
       DATAFRAME
       ====================================================== */

    div[data-testid="stDataFrame"] {

        border:
            1px solid
            rgba(0, 200, 255, 0.12);

        border-radius: 12px;

        overflow: hidden;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {

        text-align: center;

        color: #718096;

        font-size: 0.8rem;

        padding-top: 25px;

        padding-bottom: 15px;

        line-height: 1.7;
    }


    /* ======================================================
       SECTION DIVIDER
       ====================================================== */

    hr {

        border-color:
            rgba(0, 200, 255, 0.10);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD ALERT DATA
# ============================================================

df = load_alerts()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    if LOGO_PATH.exists():

        st.image(
            str(LOGO_PATH),
            width=210
        )

    st.markdown("---")

    st.markdown(
        "### 🛰️ SYSTEM"
    )

    st.success(
        "ONLINE"
    )

    st.markdown(
        "**Monitoring Mode**"
    )

    st.write(
        "READ-ONLY / PASSIVE"
    )

    st.markdown(
        "**Threat Engines**"
    )

    st.write(
        "6"
    )

    st.markdown("---")

    st.markdown(
        "### ⚙️ DATA SOURCE"
    )

    if ALERT_FILE.exists():

        st.success(
            "Alert store connected"
        )

    else:

        st.warning(
            "No alert store found"
        )

    if BENCHMARK_FILE.exists():

        st.success(
            "Benchmark report connected"
        )

    else:

        st.warning(
            "Benchmark report unavailable"
        )

    st.markdown("---")

    if st.button(
        "🔄 Refresh Dashboard",
        use_container_width=True
    ):

        st.rerun()

    st.markdown("---")

    st.caption(
        "CYBER-ASTRA\n\n"
        "AI-Based Detection of Cyber Threats "
        "in Unidirectional IP Traffic"
    )


# ============================================================
# HEADER
# ============================================================

render_header_logo()


st.info(
    "🔒 READ-ONLY MONITORING MODE — "
    "CYBER-ASTRA analyzes passively collected traffic metadata only. "
    "No probing, no return path, no payload decryption, "
    "and no mitigation commands."
)


st.markdown(
    """
    <h2 style="
        text-align:center;
        margin-bottom:4px;
    ">
        Security Operations Center
    </h2>

    <p style="
        text-align:center;
        color:#8ea0b8;
        margin-top:0px;
    ">
        AI-Based Detection of Cyber Threats in Unidirectional IP Traffic
    </p>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="status-box">
        🟢 <b>SYSTEM ONLINE</b>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        PASSIVE MONITORING
        &nbsp;&nbsp;|&nbsp;&nbsp;
        READ-ONLY INGESTION
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    "**ONE-WAY TRAFFIC**  →  "
    "**AI ANALYSIS**  →  "
    "**THREAT DETECTION**  →  "
    "**EVIDENCE-BASED ALERT**"
)


# ============================================================
# SOC KPI METRICS
# ============================================================

if df.empty:

    total_alerts = 0
    high_alerts = 0
    medium_alerts = 0
    low_alerts = 0

else:

    total_alerts = len(df)

    severity_series = (
        df["severity"]
        .astype(str)
        .str.upper()
    )

    high_alerts = int(
        (
            severity_series == "HIGH"
        ).sum()
    )

    medium_alerts = int(
        (
            severity_series == "MEDIUM"
        ).sum()
    )

    low_alerts = int(
        (
            severity_series == "LOW"
        ).sum()
    )


st.markdown(
    """
    <div style="
        margin-top:8px;
        margin-bottom:10px;
        color:#8ea0b8;
        font-size:0.78rem;
        font-weight:700;
        letter-spacing:1.5px;
        text-transform:uppercase;
    ">
        SOC STATUS OVERVIEW
    </div>
    """,
    unsafe_allow_html=True,
)


m1, m2, m3, m4, m5 = st.columns(5)


with m1:

    st.metric(
        "🚨 ACTIVE ALERTS",
        total_alerts
    )


with m2:

    st.metric(
        "🔴 HIGH SEVERITY",
        high_alerts
    )


with m3:

    st.metric(
        "🟠 MEDIUM",
        medium_alerts
    )


with m4:

    st.metric(
        "🟢 LOW",
        low_alerts
    )


with m5:

    st.metric(
        "🛡️ THREAT ENGINES",
        EXPECTED_THREAT_COUNT
    )


st.markdown(
    """
    <div style="
        height:4px;
        margin-top:12px;
        margin-bottom:8px;
        border-radius:4px;
        background:
            linear-gradient(
                90deg,
                rgba(0,220,255,0.0),
                rgba(0,220,255,0.35),
                rgba(0,220,255,0.0)
            );
    "></div>
    """,
    unsafe_allow_html=True,
)


st.divider()


# ============================================================
# THREAT DETECTION ENGINES
# ============================================================

st.markdown(
    "### 🛡️ Threat Detection Engines"
)

st.caption(
    "Six passive detection engines operating on one-way traffic metadata"
)


engines = [

    (
        "🔴",
        "DDoS / FLOODING",
        "Traffic-rate & protocol anomaly detection"
    ),

    (
        "🟣",
        "BOTNET C2",
        "Periodic flow timing & beaconing analysis"
    ),

    (
        "🟡",
        "DGA / DNS",
        "Entropy & query-length anomaly detection"
    ),

    (
        "🔵",
        "ENCRYPTED SESSION",
        "TLS/QUIC metadata analysis"
    ),

    (
        "🟠",
        "RECONNAISSANCE",
        "Destination fan-out analysis"
    ),

    (
        "🟢",
        "DATA EXFILTRATION",
        "Outbound/inbound volume asymmetry"
    ),
]


engine_cols = st.columns(3)


for i, (
    icon,
    name,
    description
) in enumerate(engines):

    with engine_cols[i % 3]:

        with st.container(border=True):

            st.markdown(
                f"### {icon} {name}"
            )

            st.caption(
                description
            )

            st.markdown(
                "🟢 **ACTIVE**  ·  "
                "**PASSIVE**  ·  "
                "**READ-ONLY**"
            )


st.divider()


# ============================================================
# THREAT FILTERS
# ============================================================

if not df.empty:

    st.markdown(
        "### 🎛️ Threat Filters"
    )

    f1, f2, f3 = st.columns(3)


    with f1:

        threat_options = [
            "ALL"
        ]

        if "threat_class" in df.columns:

            threat_options += sorted(
                df["threat_class"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        selected_threat = st.selectbox(
            "Threat Class",
            threat_options
        )


    with f2:

        severity_options = [
            "ALL"
        ]

        if "severity" in df.columns:

            severity_options += sorted(
                df["severity"]
                .dropna()
                .astype(str)
                .str.upper()
                .unique()
                .tolist()
            )

        selected_severity = st.selectbox(
            "Severity",
            severity_options
        )


    with f3:

        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05
        )


    filtered_df = df.copy()


    if selected_threat != "ALL":

        filtered_df = filtered_df[
            filtered_df[
                "threat_class"
            ]
            .astype(str)
            == selected_threat
        ]


    if selected_severity != "ALL":

        filtered_df = filtered_df[
            filtered_df[
                "severity"
            ]
            .astype(str)
            .str.upper()
            == selected_severity
        ]


    if "confidence" in filtered_df.columns:

        filtered_df = filtered_df[
            pd.to_numeric(
                filtered_df["confidence"],
                errors="coerce"
            )
            .fillna(0)
            >= min_confidence
        ]

else:

    filtered_df = df


# ============================================================
# THREAT INTELLIGENCE CHARTS
# ============================================================

if not filtered_df.empty:

    st.markdown(
        "### 📊 Threat Intelligence Overview"
    )

    chart1, chart2 = st.columns(2)


    with chart1:

        threat_counts = (
            filtered_df[
                "threat_class"
            ]
            .value_counts()
            .reset_index()
        )

        threat_counts.columns = [
            "Threat Class",
            "Count"
        ]


        fig_threat = px.bar(
            threat_counts,
            x="Threat Class",
            y="Count",
            title="Threat Distribution",
            template="plotly_dark"
        )


        fig_threat.update_layout(
            xaxis_title=None,
            yaxis_title="Alerts",
            height=380
        )


        st.plotly_chart(
            fig_threat,
            use_container_width=True
        )


    with chart2:

        severity_counts = (
            filtered_df[
                "severity"
            ]
            .astype(str)
            .str.upper()
            .value_counts()
            .reset_index()
        )

        severity_counts.columns = [
            "Severity",
            "Count"
        ]


        fig_severity = px.pie(
            severity_counts,
            names="Severity",
            values="Count",
            title="Alert Severity",
            template="plotly_dark",
            hole=0.45
        )


        fig_severity.update_layout(
            height=380
        )


        st.plotly_chart(
            fig_severity,
            use_container_width=True
        )


# ============================================================
# SECURITY ALERT FEED
# ============================================================

st.divider()

st.markdown(
    "### 🚨 Security Alert Feed"
)

st.caption(
    "Evidence-based alerts generated from passive, read-only traffic analysis."
)


if filtered_df.empty:

    st.info(
        "No alerts match the current filters."
    )

else:

    alert_feed = filtered_df.copy()


    if "timestamp" in alert_feed.columns:

        alert_feed = alert_feed.iloc[::-1]


    for _, alert in alert_feed.iterrows():

        severity = str(
            alert.get(
                "severity",
                "UNKNOWN"
            )
        ).upper()


        threat = str(
            alert.get(
                "threat_class",
                "Unknown Threat"
            )
        )


        confidence = safe_float(
            alert.get(
                "confidence",
                0
            )
        )


        ml_score = safe_float(
            alert.get(
                "ml_anomaly_score",
                0
            )
        )


        timestamp = str(
            alert.get(
                "timestamp",
                "Unknown time"
            )
        )


        flow_id = str(
            alert.get(
                "flow_id",
                "unknown"
            )
        )


        src_ip = str(
            alert.get(
                "src_ip",
                "unknown"
            )
        )


        dst_ip = str(
            alert.get(
                "dst_ip",
                "unknown"
            )
        )


        evidence = str(
            alert.get(
                "evidence",
                "No supporting evidence available."
            )
        )


        if severity == "CRITICAL":

            severity_icon = "🔴"

        elif severity == "HIGH":

            severity_icon = "🟠"

        elif severity == "MEDIUM":

            severity_icon = "🟡"

        else:

            severity_icon = "🟢"


        st.markdown(
            f"""
**{severity_icon} {severity} — {threat}**

`Flow: {flow_id}`  •  `Confidence: {confidence:.0%}`  •  `ML anomaly: {ml_score:.0%}`

**Source:** `{src_ip}` → **Destination:** `{dst_ip}`

**Evidence:** {evidence}

🕒 `{timestamp}`
"""
        )

        st.divider()


# ============================================================
# OFFLINE TRAFFIC STREAM REPLAY
# ============================================================

st.divider()

st.markdown(
    "### 🔄 Offline Traffic Stream Replay"
)

st.caption(
    "Replays previously collected flow records one at a time "
    "to demonstrate incremental near-real-time passive detection."
)


replay_col1, replay_col2 = st.columns(
    [3, 1]
)


with replay_col1:

    st.markdown(
        "**Replay Mode:** "
        "Offline • Read-Only • Passive"
    )


with replay_col2:

    st.markdown(
        "**Source:** `validation_flows.csv`"
    )


st.markdown("")


if st.button(
    "▶️ Start Traffic Replay",
    use_container_width=True
):

    replay_file = (
        BASE_DIR
        / "data"
        / "validation_flows.csv"
    )


    if not replay_file.exists():

        st.error(
            "Validation replay file not found."
        )


    else:

        try:

            from ingestion.csv_ingest import (
                load_flow_csv
            )

            from features.engine import (
                calculate_features
            )

            from detectors.engine import (
                analyze_dataframe
            )


            replay_df = load_flow_csv(
                str(replay_file)
            )


            total_flows = len(
                replay_df
            )


            progress_bar = st.progress(
                0
            )

            status_box = st.empty()


            for i in range(
                total_flows
            ):

                flow = replay_df.iloc[
                    i:i + 1
                ].copy()


                start_time = (
                    time.perf_counter()
                )


                features = calculate_features(
                    flow
                )


                detections = analyze_dataframe(
                    features
                )


                processing_time = (
                    time.perf_counter()
                    - start_time
                ) * 1000


                progress = (
                    i + 1
                ) / total_flows


                progress_bar.progress(
                    progress
                )


                status_box.markdown(
                    f"**Processing Flow "
                    f"{i + 1} / "
                    f"{total_flows}**"
                )


                if detections.empty:

                    st.success(
                        f"🟢 Flow "
                        f"{i + 1:02d} — "
                        "No threat detected"
                    )


                else:

                    alert = detections.iloc[
                        0
                    ]


                    threat = str(
                        alert.get(
                            "threat_class",
                            "Unknown"
                        )
                    )


                    severity = str(
                        alert.get(
                            "severity",
                            "UNKNOWN"
                        )
                    ).upper()


                    confidence = safe_float(
                        alert.get(
                            "confidence",
                            0
                        )
                    )


                    evidence = str(
                        alert.get(
                            "evidence",
                            "No evidence available."
                        )
                    )


                    if severity == "CRITICAL":

                        icon = "🔴"

                    elif severity == "HIGH":

                        icon = "🟠"

                    elif severity == "MEDIUM":

                        icon = "🟡"

                    else:

                        icon = "🟢"


                    st.markdown(
                        f"""
### {icon} THREAT DETECTED

**{threat}**

**Severity:** `{severity}`  
**Confidence:** `{confidence:.0%}`  
**Processing Time:** `{processing_time:.2f} ms`

**Evidence**

{evidence}
"""
                    )


                st.divider()


            status_box.success(
                f"✅ Replay completed — "
                f"{total_flows} flows processed."
            )


        except Exception as error:

            st.error(
                f"Replay failed: {error}"
            )


# ============================================================
# PERFORMANCE & VALIDATION
# ============================================================

st.divider()

st.markdown(
    "### ⚡ Performance & Validation"
)

st.caption(
    "Offline synthetic benchmark used to validate processing throughput "
    "and required threat-class coverage."
)


if BENCHMARK_FILE.exists():

    try:

        with open(
            BENCHMARK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            benchmark = json.load(
                file
            )


        counts = benchmark.get(
            "counts",
            {}
        )


        kpis = benchmark.get(
            "performance_kpis",
            {}
        )


        coverage = benchmark.get(
            "threat_coverage",
            {}
        )


        benchmark_type = benchmark.get(
            "benchmark_type",
            "Offline synthetic replay"
        )


        target_throughput = benchmark.get(
            "target_throughput_fps",
            100.0
        )


        flows_analyzed = counts.get(
            "flows_analyzed",
            0
        )


        alerts_generated = counts.get(
            "alerts_generated",
            0
        )


        throughput = kpis.get(
            "throughput_fps",
            0
        )


        avg_processing = kpis.get(
            "avg_processing_ms_per_flow",
            0
        )


        target_achieved = kpis.get(
            "target_achieved",
            False
        )


        st.caption(
            f"Benchmark type: {benchmark_type}. "
            "This measures offline synthetic replay performance "
            "on the development machine."
        )


        b1, b2, b3, b4 = st.columns(4)


        with b1:

            st.metric(
                "Flows Processed",
                f"{flows_analyzed:,}"
            )


        with b2:

            st.metric(
                "Alerts Generated",
                f"{alerts_generated:,}"
            )


        with b3:

            st.metric(
                "Throughput",
                f"{throughput:,.2f} flows/s"
            )


        with b4:

            st.metric(
                "Avg Processing Cost",
                f"{avg_processing:.3f} ms/flow"
            )


        if target_achieved:

            st.success(
                f"✅ Benchmark target achieved — "
                f"{throughput:,.2f} flows/sec measured "
                f"against a defined prototype target of "
                f"{target_throughput:,.0f} flows/sec."
            )

        else:

            st.warning(
                f"⚠️ Benchmark target not achieved — "
                f"{throughput:,.2f} flows/sec measured "
                f"against a target of "
                f"{target_throughput:,.0f} flows/sec."
            )


        st.caption(
            "Important: this is an offline synthetic benchmark, "
            "not a production network-throughput guarantee."
        )


        # ----------------------------------------------------
        # SIX THREAT VALIDATION
        # ----------------------------------------------------

        st.markdown(
            "#### 🛡️ Six-Threat Validation Coverage"
        )


        expected_threats = [

            "Volumetric / Protocol DDoS",

            "Botnet C2 Beaconing",

            "DGA Domains / DNS Tunnelling",

            "Malware in Encrypted Session",

            "Reconnaissance / Port Scanning",

            "Data Exfiltration",
        ]


        validation_rows = []


        for threat in expected_threats:

            alert_count = coverage.get(
                threat,
                0
            )


            detected = (
                alert_count > 0
            )


            validation_rows.append(
                {
                    "Threat Class":
                        threat,

                    "Detections":
                        alert_count,

                    "Validation Result":
                        (
                            "✅ DETECTED"
                            if detected
                            else "❌ NOT DETECTED"
                        ),
                }
            )


        validation_df = pd.DataFrame(
            validation_rows
        )


        st.dataframe(
            validation_df,
            use_container_width=True,
            hide_index=True
        )


        detected_count = sum(
            coverage.get(
                threat,
                0
            ) > 0
            for threat in expected_threats
        )


        if (
            detected_count
            == EXPECTED_THREAT_COUNT
        ):

            st.success(
                f"Validation coverage: "
                f"{detected_count}/"
                f"{EXPECTED_THREAT_COUNT} "
                "required threat classes exercised successfully."
            )

        else:

            st.warning(
                f"Validation coverage: "
                f"{detected_count}/"
                f"{EXPECTED_THREAT_COUNT} "
                "threat classes detected."
            )


    except Exception as error:

        st.error(
            f"Unable to load benchmark report: {error}"
        )


else:

    st.info(
        "No benchmark report found. "
        "Run `python benchmark.py` to generate one."
    )


# ============================================================
# ALERT INVESTIGATION
# ============================================================

st.divider()

st.markdown(
    "### 🔎 Alert Investigation"
)

st.caption(
    "Detailed inspection of the selected evidence-based detection."
)


if filtered_df.empty:

    st.info(
        "No alert available for investigation."
    )


else:

    selected_index = st.selectbox(
        "Select an alert to investigate",
        filtered_df.index,
        format_func=lambda index: (
            f"{filtered_df.loc[index, 'threat_class']} | "
            f"{filtered_df.loc[index, 'src_ip']} → "
            f"{filtered_df.loc[index, 'dst_ip']}"
        )
    )


    selected_alert = filtered_df.loc[
        selected_index
    ]


    threat = str(
        selected_alert.get(
            "threat_class",
            "Unknown Threat"
        )
    )


    severity = str(
        selected_alert.get(
            "severity",
            "UNKNOWN"
        )
    ).upper()


    confidence = safe_float(
        selected_alert.get(
            "confidence",
            0
        )
    )


    ml_score = safe_float(
        selected_alert.get(
            "ml_anomaly_score",
            0
        )
    )


    if severity == "CRITICAL":

        severity_icon = "🔴"

    elif severity == "HIGH":

        severity_icon = "🟠"

    elif severity == "MEDIUM":

        severity_icon = "🟡"

    else:

        severity_icon = "🟢"


    st.markdown(
        f"### {severity_icon} {severity} — {threat}"
    )


    # --------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Detector Confidence",
            f"{confidence:.0%}"
        )


    with col2:

        st.metric(
            "ML Anomaly Score",
            f"{ml_score:.0%}"
        )


    with col3:

        st.metric(
            "Status",
            str(
                selected_alert.get(
                    "status",
                    "NEW"
                )
            )
        )


    with col4:

        st.metric(
            "Severity",
            severity
        )


    # --------------------------------------------------------
    # FLOW INFORMATION
    # --------------------------------------------------------

    st.markdown(
        "#### 🌐 Flow Information"
    )


    flow_col1, flow_col2 = st.columns(2)


    with flow_col1:

        st.markdown(
            "**Source**"
        )

        st.code(
            str(
                selected_alert.get(
                    "src_ip",
                    "Unknown"
                )
            )
        )


    with flow_col2:

        st.markdown(
            "**Destination**"
        )

        st.code(
            str(
                selected_alert.get(
                    "dst_ip",
                    "Unknown"
                )
            )
        )


    flow_col3, flow_col4 = st.columns(2)


    with flow_col3:

        st.markdown(
            "**Flow ID**"
        )

        st.code(
            str(
                selected_alert.get(
                    "flow_id",
                    "Unknown"
                )
            )
        )


    with flow_col4:

        st.markdown(
            "**Timestamp**"
        )

        st.code(
            str(
                selected_alert.get(
                    "timestamp",
                    "Unknown"
                )
            )
        )


    # --------------------------------------------------------
    # SUPPORTING EVIDENCE
    # --------------------------------------------------------

    st.markdown(
        "#### 🧾 Supporting Evidence"
    )


    st.info(
        str(
            selected_alert.get(
                "evidence",
                "No evidence available."
            )
        )
    )


# ============================================================
# AI ANALYST
# ============================================================

st.divider()

st.markdown(
    "### 🤖 CYBER-ASTRA AI Analyst"
)

st.caption(
    "Qwen3-powered passive analysis of the selected security alert."
)


status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    st.success(
        "🟢 AI ANALYST READY"
    )


with status_col2:

    st.info(
        f"🧠 MODEL: {OLLAMA_MODEL}"
    )


with status_col3:

    st.info(
        "🔒 PASSIVE ANALYSIS"
    )


st.markdown("")


if not filtered_df.empty:

    ai_col1, ai_col2 = st.columns(
        [2, 1]
    )


    with ai_col1:

        st.markdown(
            "#### 🎯 Selected Alert"
        )

        st.markdown(
            f"""
**Threat:** `{selected_alert.get("threat_class", "Unknown")}`

**Severity:** `{selected_alert.get("severity", "Unknown")}`

**Flow ID:** `{selected_alert.get("flow_id", "Unknown")}`
"""
        )


    with ai_col2:

        st.metric(
            "Detection Confidence",
            f"{confidence:.0%}"
        )

        st.metric(
            "ML Anomaly Score",
            f"{ml_score:.0%}"
        )


    st.markdown("")


    # --------------------------------------------------------
    # QWEN3 ANALYSIS
    # --------------------------------------------------------

    if st.button(
        "🧠 Analyze Selected Alert with Qwen3",
        use_container_width=True
    ):

        prompt = f"""
You are the local AI analyst inside CYBER-ASTRA,
a read-only cybersecurity monitoring platform.

Analyze the security alert using ONLY the supplied alert data.

IMPORTANT RULES:

- Do not invent facts that are not provided.
- Do not claim that an alert proves compromise.
- Treat detector confidence as detection confidence, not certainty.
- Treat the ML anomaly score as an anomaly indicator, not a probability of attack.
- Do not combine the scores into a fake probability.
- Do not recommend active probing, scanning, blocking, or network modification.
- Do not perform any network action.
- Clearly separate observed evidence from interpretation.
- Keep the response concise and suitable for a SOC analyst.
- Investigation suggestions must remain passive and metadata-based.

ALERT INFORMATION

Threat Class:
{selected_alert.get("threat_class", "Unknown")}

Severity:
{selected_alert.get("severity", "Unknown")}

Detection Confidence:
{confidence:.2f}

ML Anomaly Score:
{ml_score:.3f}

Flow ID:
{selected_alert.get("flow_id", "Unknown")}

Source IP:
{selected_alert.get("src_ip", "Unknown")}

Destination IP:
{selected_alert.get("dst_ip", "Unknown")}

Timestamp:
{selected_alert.get("timestamp", "Unknown")}

Supporting Evidence:
{selected_alert.get("evidence", "None")}

Return the result using exactly these sections:

### Detection Summary
Briefly explain what the detection engine observed.

### Evidence
List the concrete evidence provided by the detection engine.

### ML Anomaly Interpretation
Explain what the ML anomaly score indicates.
Do not describe it as an attack probability or accuracy percentage.

### Confidence Interpretation
Explain what the detector confidence indicates without treating it as proof of compromise.

### Investigation Focus
Give 2-3 passive investigation areas using available traffic records or metadata.

### Analyst Note
Give one concise sentence describing how a SOC analyst should interpret this alert.
"""


        st.markdown(
            "#### 🧠 Qwen3 Analyst Assessment"
        )


        with st.spinner(
            "Qwen3 is analyzing the selected alert..."
        ):

            try:

                headers = {
                    "Content-Type":
                        "application/json"
                }


                if OLLAMA_API_KEY:

                    headers[
                        "Authorization"
                    ] = (
                        f"Bearer {OLLAMA_API_KEY}"
                    )


                # ------------------------------------------------
                # OLLAMA CHAT API
                # ------------------------------------------------

                if OLLAMA_URL.rstrip(
                    "/"
                ).endswith(
                    "/api/chat"
                ):

                    payload = {

                        "model":
                            OLLAMA_MODEL,

                        "messages": [

                            {
                                "role":
                                    "user",

                                "content":
                                    prompt,
                            }
                        ],

                        "stream":
                            True,

                        "think":
                            False,

                        "options": {

                            "temperature":
                                0.1,

                            "num_predict":
                                180,

                            "num_ctx":
                                2048,
                        },
                    }


                # ------------------------------------------------
                # OLLAMA GENERATE API
                # ------------------------------------------------

                else:

                    payload = {

                        "model":
                            OLLAMA_MODEL,

                        "prompt":
                            prompt,

                        "stream":
                            True,

                        "think":
                            False,

                        "options": {

                            "temperature":
                                0.1,

                            "num_predict":
                                180,

                            "num_ctx":
                                2048,
                        },
                    }


                response = requests.post(
                    OLLAMA_URL,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=(
                        10,
                        300
                    ),
                )


                response.raise_for_status()


                analysis_placeholder = (
                    st.empty()
                )


                analysis_text = ""


                for line in response.iter_lines():

                    if not line:
                        continue


                    try:

                        chunk = json.loads(
                            line.decode(
                                "utf-8"
                            )
                        )


                        token = chunk.get(
                            "response",
                            ""
                        )


                        if not token:

                            message = chunk.get(
                                "message",
                                {}
                            )


                            if isinstance(
                                message,
                                dict
                            ):

                                token = (
                                    message.get(
                                        "content",
                                        ""
                                    )
                                    or ""
                                )


                        analysis_text += (
                            str(token)
                        )


                        analysis_placeholder.markdown(
                            analysis_text
                        )


                    except Exception:

                        continue


                if not analysis_text.strip():

                    analysis_placeholder.warning(
                        "Qwen3 returned no analysis."
                    )

                else:

                    st.success(
                        "✅ Qwen3 analysis completed."
                    )


            except requests.exceptions.ConnectionError:

                st.warning(
                    "Ollama is not currently reachable. "
                    "Start Ollama and try again."
                )


            except requests.exceptions.Timeout:

                st.error(
                    "Qwen3 response timed out. "
                    "The local model may be running slowly on CPU. "
                    "Try again or reduce the response length."
                )


            except Exception as error:

                st.error(
                    f"AI Analyst error: {error}"
                )


else:

    st.info(
        "Generate or load an alert before using the AI Analyst."
    )


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.markdown(
    "### 🔐 CYBER-ASTRA Detection Architecture"
)

st.caption(
    "End-to-end passive detection pipeline for unidirectional IP traffic."
)


st.markdown(
    """
<div style="
    padding:24px;
    border-radius:16px;
    border:1px solid rgba(120,120,120,0.25);
    background:rgba(30,30,30,0.35);
">

<div style="text-align:center;">

<h4>📡 ONE-WAY TRAFFIC</h4>

<p>
Passive flow records / mirrored traffic
</p>

<h3>↓</h3>

<h4>🔒 READ-ONLY INGESTION</h4>

<p>
No return path • No active probing
</p>

<h3>↓</h3>

<h4>⚙️ FEATURE EXTRACTION</h4>

<p>
Flow rate • timing • byte ratios • entropy • metadata
</p>

<h3>↓</h3>

</div>


<div style="
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:12px;
    margin:20px 0;
">


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>🛡️ DDoS</b><br>

<small>
Traffic intensity
</small>

</div>


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>🤖 C2</b><br>

<small>
Flow periodicity
</small>

</div>


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>🌐 DGA / DNS</b><br>

<small>
Entropy & length
</small>

</div>


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>🔐 ENCRYPTED</b><br>

<small>
TLS metadata
</small>

</div>


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>🔎 RECON</b><br>

<small>
Destination fan-out
</small>

</div>


<div style="
    padding:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.15);
    border-radius:10px;
">

<b>📤 EXFIL</b><br>

<small>
Traffic asymmetry
</small>

</div>


</div>


<div style="text-align:center;">

<h3>↓</h3>

<h4>🧠 DETECTION + SCORING</h4>

<p>
Rule-based threat engines + ML anomaly detection
</p>

<h3>↓</h3>

<h4>🧾 EVIDENCE-BASED ALERT</h4>

<p>
Threat class • confidence • evidence • timestamp • flow ID
</p>

<h3>↓</h3>

<h4>🤖 QWEN3 AI ANALYST</h4>

<p>
Passive alert interpretation and investigation focus
</p>

<h3>↓</h3>

<h4>🖥️ SOC DASHBOARD</h4>

<p>
Visualization • investigation • replay • validation
</p>

</div>

</div>
""",
    unsafe_allow_html=True
)


st.markdown("")


st.info(
    "🔒 Security constraint: CYBER-ASTRA observes and analyzes traffic "
    "without probing, modifying, blocking, or sending commands back "
    "toward the monitored network."
)


# ============================================================
# FINAL CYBER-ASTRA CLOSING PANEL
# ============================================================

st.divider()

st.markdown(
    "## 🛡️ CYBER-ASTRA"
)

st.caption(
    "AI-Based Passive Cyber Threat Detection"
)

st.markdown(
    """
**ONE-WAY TRAFFIC**  
↓  
**AI ANALYSIS**  
↓  
**THREAT DETECTION**  
↓  
**EVIDENCE-BASED ALERT**
"""
)

st.success(
    "🔒 READ-ONLY • PASSIVE • EVIDENCE-BASED"
)

st.markdown(
    "**HACK-ASTRA • SIH26145**"
)

st.caption(
    "Detect • Analyze • Defend"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        CYBER-ASTRA • HACK-ASTRA • SIH26145<br>
        Read-only passive cyber-threat detection
    </div>
    """,
    unsafe_allow_html=True,
)