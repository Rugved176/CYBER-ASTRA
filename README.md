# CYBER-ASTRA 🛡️

### AI-Powered Cyber Threat Detection for Unidirectional IP Traffic

CYBER-ASTRA is an AI-driven, read-only cybersecurity platform designed to
detect and analyze cyber threats from passively observed network traffic
without establishing a return path to the monitored production network.

The platform is designed for security environments where traffic is delivered
to an isolated monitoring enclave through passive mirroring or a hardware
data diode. CYBER-ASTRA analyzes network-flow and traffic metadata to identify
suspicious behavioral patterns and generate evidence-based security alerts.

## Core Capabilities

- Near-real-time network traffic analysis
- Read-only and passive monitoring architecture
- AI/ML-based anomaly detection
- Flow-level feature engineering
- Evidence-based threat alerts
- Confidence and anomaly scoring
- Interactive SOC-style dashboard
- Offline traffic replay and validation
- Encrypted-session metadata analysis without payload decryption

## Threat Detection

CYBER-ASTRA currently analyzes behavioral indicators associated with:

1. Volumetric / Protocol DDoS
2. Botnet C2 Beaconing
3. DGA Domains / DNS Tunnelling
4. Malware in Encrypted Sessions
5. Reconnaissance / Port Scanning
6. Data Exfiltration

## Detection Pipeline

Unidirectional Traffic
→ Passive Ingestion
→ Feature Extraction
→ AI/ML Analysis
→ Threat Detection
→ Confidence + Evidence
→ Security Alert
→ SOC Dashboard

## Technology Stack

- Python
- Streamlit
- Pandas / NumPy
- Scikit-learn
- Isolation Forest
- Plotly
- Pydantic
- Ollama / Qwen3
- PCAP / Flow Metadata
- JSON / CSV / Parquet

## Security Design Principles

CYBER-ASTRA follows a defensive, passive-monitoring architecture:

- No active probing
- No return communication to monitored systems
- No inline blocking or mitigation commands
- No payload decryption
- Metadata-first analysis
- Evidence-based alert generation
- Isolated monitoring workflow

The project is being developed as a prototype for cybersecurity monitoring
of critical infrastructure and other high-security network environments.