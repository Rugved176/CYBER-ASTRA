import json
import os
import requests
import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

# app.py is located directly inside D:\CYBER-ASTRA
BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = BASE_DIR / "assets" / "cyber_astra_logo.png"
ALERT_FILE = BASE_DIR / "data" / "alerts.json"
BENCHMARK_FILE = BASE_DIR / "data" / "benchmark_report.json"

OLLAMA_URL = "https://ollama.com/api/chat"
OLLAMA_API_KEY = None
OLLAMA_MODEL = "qwen3:14b"

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
    """
    Convert the CYBER-ASTRA logo to base64 so it can be
    displayed cleanly inside custom HTML.
    """

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
    """
    Render the actual CYBER-ASTRA logo in the dashboard header.
    """

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

        alerts = data.get("alerts", [])

        if not alerts:
            return pd.DataFrame()

        return pd.DataFrame(alerts)

    except Exception as error:

        st.error(
            f"Unable to load alerts: {error}"
        )

        return pd.DataFrame()


# ============================================================
# CUSTOM CSS
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

    h1, h2, h3 {
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
            1px solid rgba(0, 200, 255, 0.15);
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
                0 0 14px rgba(0, 160, 255, 0.18)
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
            1px solid rgba(0, 230, 150, 0.28);

        margin-bottom: 20px;

        box-shadow:
            0 0 18px rgba(0, 220, 150, 0.03);
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
            1px solid rgba(0, 200, 255, 0.18);

        border-radius: 14px;
        padding: 14px;

        box-shadow:
            0 0 20px rgba(0, 140, 255, 0.05);
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {

        border-radius: 10px;

        border:
            1px solid rgba(0, 200, 255, 0.35);

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
            0 0 14px rgba(0, 180, 255, 0.10);
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
            1px solid rgba(0, 200, 255, 0.15);

        margin-bottom: 10px;
    }


    /* ======================================================
       DATAFRAME
       ====================================================== */

    div[data-testid="stDataFrame"] {

        border:
            1px solid rgba(0, 200, 255, 0.12);

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

    # Actual CYBER-ASTRA logo
    if LOGO_PATH.exists():

        st.image(
            str(LOGO_PATH),
            width=210
        )

    st.markdown("---")

    st.markdown("### 🛰️ SYSTEM")

    st.success("ONLINE")

    st.markdown("**Monitoring Mode**")
    st.write("READ-ONLY / PASSIVE")

    st.markdown("**Threat Engines**")
    st.write("6")

    st.markdown("---")

    st.markdown("### ⚙️ DATA SOURCE")

    if ALERT_FILE.exists():

        st.success("Alert store connected")

    else:

        st.warning("No alert store found")

    if BENCHMARK_FILE.exists():

        st.success("Benchmark report connected")

    else:

        st.warning("Benchmark report unavailable")

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
    <h2 style="text-align:center; margin-bottom:4px;">
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


# ============================================================
# ALERT METRICS
# ============================================================

if df.empty:

    total_alerts = 0
    high_alerts = 0
    medium_alerts = 0
    low_alerts = 0

else:

    total_alerts = len(df)

    high_alerts = len(
        df[
            df["severity"]
            .astype(str)
            .str.upper()
            == "HIGH"
        ]
    )

    medium_alerts = len(
        df[
            df["severity"]
            .astype(str)
            .str.upper()
            == "MEDIUM"
        ]
    )

    low_alerts = len(
        df[
            df["severity"]
            .astype(str)
            .str.upper()
            == "LOW"
        ]
    )


m1, m2, m3, m4, m5 = st.columns(5)

m1.metric(
    "🚨 Total Alerts",
    total_alerts
)

m2.metric(
    "🔴 HIGH",
    high_alerts
)

m3.metric(
    "🟠 MEDIUM",
    medium_alerts
)

m4.metric(
    "🟢 LOW",
    low_alerts
)

m5.metric(
    "🛡️ Threat Engines",
    EXPECTED_THREAT_COUNT
)


st.divider()


# ============================================================
# FILTERS
# ============================================================

if not df.empty:

    st.markdown("### 🎛️ Threat Filters")

    f1, f2, f3 = st.columns(3)

    with f1:

        threat_options = ["ALL"]

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

        severity_options = ["ALL"]

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
            filtered_df["threat_class"]
            .astype(str)
            == selected_threat
        ]

    if selected_severity != "ALL":

        filtered_df = filtered_df[
            filtered_df["severity"]
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
# DASHBOARD CHARTS
# ============================================================

if not filtered_df.empty:

    st.markdown(
        "### 📊 Threat Intelligence Overview"
    )

    chart1, chart2 = st.columns(2)

    # --------------------------------------------------------
    # Threat Distribution
    # --------------------------------------------------------

    with chart1:

        threat_counts = (
            filtered_df["threat_class"]
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

    # --------------------------------------------------------
    # Severity Distribution
    # --------------------------------------------------------

    with chart2:

        severity_counts = (
            filtered_df["severity"]
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

st.markdown("### 🚨 Security Alert Feed")

if filtered_df.empty:

    st.info(
        "No alerts match the current filters."
    )

else:

    display_columns = [
        "timestamp",
        "flow_id",
        "threat_class",
        "severity",
        "confidence",
        "ml_anomaly_score",
        "src_ip",
        "dst_ip",
        "evidence",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    display_df = filtered_df[
        available_columns
    ].copy()

    if "confidence" in display_df.columns:

        display_df["confidence"] = (
            pd.to_numeric(
                display_df["confidence"],
                errors="coerce"
            )
            .fillna(0)
            .mul(100)
            .round(1)
            .astype(str)
            + "%"
        )

    if "ml_anomaly_score" in display_df.columns:

        display_df["ml_anomaly_score"] = (
            pd.to_numeric(
                display_df["ml_anomaly_score"],
                errors="coerce"
            )
            .fillna(0)
            .mul(100)
            .round(1)
            .astype(str)
            + "%"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )


# ============================================================
# OFFLINE STREAM REPLAY
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
    [2, 1]
)

with replay_col1:

    replay_delay = st.slider(
        "Replay interval (seconds)",
        min_value=0.1,
        max_value=3.0,
        value=0.5,
        step=0.1,
        key="replay_delay"
    )

with replay_col2:

    replay_start = st.button(
        "▶ Start Replay",
        use_container_width=True
    )


if replay_start:

    try:

        from replay import replay_flows

        replay_placeholder = st.empty()

        progress_bar = st.progress(0)

        replay_results = []

        replay_total = 6

        for result in replay_flows(
            delay=replay_delay
        ):

            replay_results.append(result)

            flow_number = result[
                "flow_number"
            ]

            flow_id = result.get(
                "flow_id",
                "unknown"
            )

            processing_time = result.get(
                "processing_time_ms",
                0
            )

            alerts = result[
                "alerts"
            ]

            with replay_placeholder.container():

                st.markdown(
                    f"**Processing Flow {flow_number} / "
                    f"{replay_total}**"
                )

                st.caption(
                    f"Flow ID: `{flow_id}`  |  "
                    f"Processing cost: "
                    f"`{processing_time:.3f} ms`"
                )

                if alerts:

                    st.success(
                        f"Threat detected — "
                        f"{len(alerts)} alert(s)"
                    )

                    for alert in alerts:

                        st.warning(
                            f"**{alert.get('threat_class', 'Unknown')}** "
                            f"| Severity: "
                            f"{alert.get('severity', 'Unknown')} "
                            f"| Confidence: "
                            f"{float(alert.get('confidence', 0)) * 100:.1f}%"
                        )

                        st.caption(
                            alert.get(
                                "evidence",
                                "No evidence available."
                            )
                        )

                else:

                    st.info(
                        "No threat detected for this flow."
                    )

            progress_bar.progress(
                min(
                    flow_number / replay_total,
                    1.0
                )
            )

        if replay_results:

            replay_times = [
                result.get(
                    "processing_time_ms",
                    0
                )
                for result in replay_results
            ]

            avg_replay_time = (
                sum(replay_times)
                / len(replay_times)
            )

            max_replay_time = max(
                replay_times
            )

            st.success(
                f"Replay complete — "
                f"{len(replay_results)} flows processed."
            )

            rc1, rc2 = st.columns(2)

            with rc1:

                st.metric(
                    "Replay Avg Processing",
                    f"{avg_replay_time:.3f} ms"
                )

            with rc2:

                st.metric(
                    "Replay Max Processing",
                    f"{max_replay_time:.3f} ms"
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


if BENCHMARK_FILE.exists():

    try:

        with open(
            BENCHMARK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            benchmark = json.load(file)

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

            detected = alert_count > 0

            validation_rows.append(
                {
                    "Threat Class": threat,
                    "Detections": alert_count,
                    "Validation Result": (
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

        if detected_count == EXPECTED_THREAT_COUNT:

            st.success(
                f"Validation coverage: "
                f"{detected_count}/{EXPECTED_THREAT_COUNT} "
                "required threat classes exercised successfully."
            )

        else:

            st.warning(
                f"Validation coverage: "
                f"{detected_count}/{EXPECTED_THREAT_COUNT} "
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

    if "flow_id" in selected_alert.index:

        st.markdown("**Flow ID**")

        st.code(
            str(
                selected_alert.get(
                    "flow_id",
                    "Unknown"
                )
            )
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        confidence = float(
            selected_alert.get(
                "confidence",
                0
            )
        )

        st.metric(
            "Detector Confidence",
            f"{confidence * 100:.1f}%"
        )

    with col2:

        ml_score = float(
            selected_alert.get(
                "ml_anomaly_score",
                0
            )
        )

        st.metric(
            "ML Anomaly Score",
            f"{ml_score * 100:.1f}%"
        )

    with col3:

        st.metric(
            "Severity",
            str(
                selected_alert.get(
                    "severity",
                    "UNKNOWN"
                )
            )
        )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("**Threat Class**")

        st.info(
            str(
                selected_alert.get(
                    "threat_class",
                    "Unknown"
                )
            )
        )

    with c2:

        st.markdown("**Severity**")

        st.warning(
            str(
                selected_alert.get(
                    "severity",
                    "Unknown"
                )
            )
        )

    with c3:

        confidence = float(
            selected_alert.get(
                "confidence",
                0
            )
        )

        st.markdown("**Confidence**")

        st.metric(
            "Detection Confidence",
            f"{confidence * 100:.1f}%"
        )

    c4, c5 = st.columns(2)

    with c4:

        st.markdown("**Source**")

        st.code(
            str(
                selected_alert.get(
                    "src_ip",
                    "Unknown"
                )
            )
        )

    with c5:

        st.markdown("**Destination**")

        st.code(
            str(
                selected_alert.get(
                    "dst_ip",
                    "Unknown"
                )
            )
        )

    st.markdown("**Timestamp**")

    st.write(
        str(
            selected_alert.get(
                "timestamp",
                "Unknown"
            )
        )
    )

    st.markdown(
        "### 🧾 Supporting Evidence"
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

st.write(
    "Use the local Qwen3 model to interpret the selected "
    "detection evidence and summarize it for a SOC analyst."
)


if not filtered_df.empty:

    if st.button(
        "🧠 Analyze Selected Alert with Qwen3",
        use_container_width=True
    ):

        confidence = float(
            selected_alert.get(
                "confidence",
                0
            )
        )

        ml_anomaly_score = float(
            selected_alert.get(
                "ml_anomaly_score",
                0
            )
        )

        prompt = f"""
You are the local AI analyst inside CYBER-ASTRA,
a read-only cybersecurity monitoring platform.

Analyze the security alert using ONLY the supplied alert data.

IMPORTANT RULES:

- Do not invent facts that are not provided.
- Do not claim that an alert proves compromise.
- Treat the detector confidence as detection confidence, not certainty.
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
{ml_anomaly_score:.3f}

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

        with st.spinner(
            "Qwen3 is analyzing the alert..."
        ):

            try:

                response = requests.post(
  		    OLLAMA_URL,
    		    json={
        		"model": OLLAMA_MODEL,
       			"prompt": prompt,
     			"stream": True,
     			"think": False,
    			"options": {
       			   "temperature": 0.1,
            		   "num_predict": 180,
            		   "num_ctx": 2048,
        		},
    		    },
    		     stream=True,
   		     timeout=(10, 300),
		)
                response.raise_for_status()

                analysis_placeholder = st.empty()

                analysis_text = ""

                for line in response.iter_lines():

                    if not line:
                        continue

                    try:

                        chunk = json.loads(
                            line.decode("utf-8")
                        )

                        token = chunk.get(
                            "response",
                            ""
                        )

                        analysis_text += token

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
                        "Qwen3 analysis completed."
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

st.code(
    """
ONE-WAY TRAFFIC / PASSIVE FLOW RECORDS
                ↓
        READ-ONLY INGESTION
                ↓
        FEATURE EXTRACTION
                ↓
    ┌───────────┬───────────┬───────────┐
    │   DDoS    │    C2     │    DGA    │
    ├───────────┼───────────┼───────────┤
    │   TLS     │   RECON   │   EXFIL   │
    └───────────┴───────────┴───────────┘
                ↓
       DETECTION + SCORING
                ↓
       CONFIDENCE + EVIDENCE
                ↓
          ALERT STORE
                ↓
          QWEN3 AI ANALYST
                ↓
          SOC DASHBOARD
    """,
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        CYBER-ASTRA • HACK-ASTRA • SIH26145<br>
        Detect • Analyze • Defend<br>
        Read-only passive cyber-threat detection
    </div>
    """,
    unsafe_allow_html=True,
)