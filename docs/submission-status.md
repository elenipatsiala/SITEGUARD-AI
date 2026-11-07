# Submission Status

Status reflects files present in this repository snapshot.

| Deliverable | Status | Evidence or remaining work |
| --- | --- | --- |
| Public GitHub repository | Present | Source repository linked from the project owner. |
| README | Updated | Build/run notes and current implementation boundaries are documented. |
| ROS 2 mission system | Prototype present | Mission manager and synthetic hazard detector. |
| Unitree telemetry bridge | Prototype present | Optional read-only Unitree SDK 2 subscription. |
| Dashboard source | Prototype present | Streamlit UI and ROS-to-file bridge. |
| System architecture | Documented | [system-architecture.md](system-architecture.md). |
| Mission workflow | Documented | [mission-workflow.md](mission-workflow.md). |
| SDK mapping | Documented | [sdk-component-mapping.md](sdk-component-mapping.md). |
| Safety and ethics | Documented | [safety-ethics.md](safety-ethics.md). |
| MuJoCo Go2 simulation | Source included | Official Unitree Go2 MJCF and meshes, marked boxes, scripted patrol, orange-color image segmentation, optional ROS 2 publisher. Runtime execution still needs local validation. |
| Simulation demo video | Pending | Record after the simulator and ROS 2 workflow run together. Show the model, box detection, state transition, and read-only dashboard. |
| Final presentation/specification deck | Updated draft created | See `SITEGUARD-AI-specification.pptx`. Update after runtime validation and video recording. |

## Demo recording checklist

1. Show the project label and state that the run uses simulation.
2. Show the Go2 model and explain that the box detector uses an orange-color pixel mask rather than a trained object-recognition model.
3. Show the robot base following the scripted patrol, finding a box, and holding position in `SAFE_STOP` while the dashboard updates.
4. Avoid implying that the prototype performs a hardware emergency stop or validated site inspection.
5. Include a short closing frame with the prototype limitations.
