# SDK and Component Mapping

This mapping separates implemented interfaces from proposed integrations. “Implemented” means that the source code in this repository contains the component; it does not mean the component has passed hardware or simulator validation.

| Capability | Repository implementation | Interface or dependency | Status and limitation |
| --- | --- | --- | --- |
| Mission-state management | `siteguard_mission/mission_manager.py` | ROS 2 `rclpy`; `std_msgs/msg/String`; `/siteguard/hazard_status` and `/siteguard/mission_state` | Prototype; string-based states, no service/action interface, no operator confirmation. |
| MuJoCo simulation | `simulation/run_go2_box_patrol.py`, `simulation/siteguard_scene.xml`, `simulation/assets/go2/` | Google DeepMind MuJoCo Python bindings; NumPy; Unitree Go2 MJCF and mesh assets | Go2 body, joints, mesh and contacts are simulated. The base traverses a scripted kinematic path rather than an actuated gait. |
| Box detection | `simulation/run_go2_box_patrol.py` | Rendered RGB frame from `go2_front`; NumPy orange-color mask | Detects orange pixel regions and returns an image-space bounding box. No trained model, arbitrary object classes, range estimate, or safety claim. |
| Hazard input | `siteguard_mission/hazard_detector.py` | ROS 2 timer; `std_msgs/msg/String`; `/siteguard/hazard_status` | Alternate synthetic timer source. Do not run alongside the MuJoCo hazard publisher. |
| Go2 telemetry | `siteguard_mission/telemetry_bridge.py` | Unitree SDK 2 Python bindings; `ChannelSubscriber('rt/sportmodestate', SportModeState_)`; ROS 2 JSON string topic | Optional read-only adapter. SDK availability and DDS transport are external prerequisites. Code initializes the channel on `lo`. |
| Dashboard state bridge | `siteguard_mission/dashboard_bridge.py` | ROS 2 subscriptions; JSON file selected by `SITEGUARD_STATE_FILE` | Prototype; local file exchange, not a network API. |
| Mission dashboard | `dashboard.py` | Streamlit and Plotly | Read-only display; values become available only when the bridge writes state. |
| Simulation-to-ROS bridge | `RosBridge` in `simulation/run_go2_box_patrol.py` | `/siteguard/hazard_status`, `/siteguard/sim_position`, `/siteguard/go2/telemetry` | Optional `--ros2` mode. Publishes simulated state; it does not receive robot commands. |
| Unitree motion commands | None | No command publisher, SDK sport client, or motion-control API in this repository | Out of scope for this prototype. |

## Telemetry fields read by the bridge

The adapter reads `position`, `velocity`, `body_height`, `mode`, and `error_code` from the SDK's sport-mode state object and publishes them as JSON inside a ROS 2 `String`. It does not translate these into typed ROS messages or use them to control mission transitions.

## Recommended next interface step

Before adding simulator or hardware integration, define typed ROS 2 messages for hazard detections and mission state, including timestamps and validity metadata. Then document QoS, stale-data behavior, and the source of each field. Keep any future command interface separate from the read-only telemetry path and test it in simulation first.
