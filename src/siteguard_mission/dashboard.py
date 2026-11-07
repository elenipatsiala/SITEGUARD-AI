import json
import os
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="SITEGUARD-AI", page_icon="🛰️", layout="wide")

DATA_FILE = Path(
    os.environ.get(
        "SITEGUARD_STATE_FILE",
        str(Path.home() / ".local/state/siteguard/dashboard_state.json")
    )
).expanduser()
GO2_IMAGE = Path(__file__).parent / "assets" / "go2.png"

st.markdown("""
<style>
.stApp {background-color: #0b1220; color: #e5edf8;}
[data-testid="stMetric"] {
    background: #142238;
    border: 1px solid #263b58;
    padding: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

def get_state():
    data = {
        "mission_state": "WAITING",
        "hazard_status": "UNKNOWN",
        "telemetry": {},
        "updated": "No data received",
        "events": []
    }
    try:
        if DATA_FILE.exists():
            data.update(json.loads(DATA_FILE.read_text()))
    except (OSError, json.JSONDecodeError):
        pass
    return data

st.title("🛰️ SITEGUARD-AI")
st.caption("AUTONOMOUS SYSTEMS MONITORING | SIMULATION MODE")
st.divider()

@st.fragment(run_every="2s")
def live_monitor():
    state = get_state()
    mission = state.get("mission_state", "WAITING")
    hazard = state.get("hazard_status", "UNKNOWN")
    telemetry = state.get("telemetry", {})

    a, b, c = st.columns(3)
    a.metric("MISSION STATE", mission)
    b.metric("HAZARD STATUS", hazard)
    c.metric("SYSTEM MODE", "SIMULATION")

    st.subheader("Telemetry Overview")
    x, y, v = st.columns(3)
    x.metric("Position X", telemetry.get("x", "—"))
    y.metric("Position Y", telemetry.get("y", "—"))
    v.metric("Velocity", telemetry.get("velocity", "—"))

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Mission Monitor")
        if mission == "SAFE_STOP":
            st.error("Simulated safety stop active")
        elif mission == "PATROL":
            st.success("Mission running in simulation")
        else:
            st.info("Waiting for ROS 2 data")

    with right:
        st.subheader("Hazard Monitor")
        if hazard == "HAZARD_DETECTED":
            st.warning("Simulated hazard detected")
        elif hazard == "NO_HAZARD":
            st.success("No simulated hazard detected")
        else:
            st.info("Waiting for hazard data")

    st.divider()
    st.caption("Last update: " + str(state.get("updated", "Unknown")))
    st.caption("Read-only dashboard | No robot control commands")

    if st.button("Refresh dashboard"):
        st.rerun()

    st.divider()
    st.subheader("EVENT MONITOR | LIVE HISTORY")
    events = state.get("events", [])

    if events:
        for event in reversed(events):
            st.write(
                f"🕒 {event.get('time', '—')} | "
                f"{event.get('type', 'EVENT')} → "
                f"{event.get('value', '—')}"
            )
    else:
        st.info("Waiting for simulation events...")

live_monitor()

st.divider()
st.subheader("UNITREE GO2 | ROBOT VISUALIZATION")
if GO2_IMAGE.exists():
    st.image(str(GO2_IMAGE), width=420)
st.caption("Go2 model reference — static asset, not a live 3D rendering.")

st.divider()
st.subheader("MISSION MAP | PATROL ROUTE")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[0, 3, 6, 9],
    y=[0, 2, 1, 4],
    mode="lines+markers+text",
    text=["GATE", "NORTH FENCE", "STORAGE AREA", "WATER STATION"],
    textposition="top center"
))
fig.update_layout(template="plotly_dark", height=420)
st.plotly_chart(fig, use_container_width=True)
