# Safety and Ethics

## Intended use

SITEGUARD-AI is a research and demonstration prototype for human-supervised inspection concepts in construction settings. The current repository does not provide a deployed robot, a validated hazard detector, or a safety-rated control system.

## Current safeguards and boundaries

- The MuJoCo box detector segments orange pixels from the simulated camera. It does not represent real site sensing or a validated perception system. The alternate demo uses a deterministic timer.
- The dashboard displays state and telemetry but does not issue robot commands.
- The Unitree telemetry adapter is read-only.
- The `SAFE_STOP` state stops the scripted kinematic patrol and changes the ROS 2 mission label. No hardware actuator stop is performed.
- No physical robot deployment, construction-site trial, or safety validation is claimed.

## Risks that remain

- A synthetic or stale hazard signal can give a misleading impression of live perception.
- The prototype resumes `PATROL` as soon as it receives `NO_HAZARD`, without a human acknowledgement or independent clearance check.
- ROS 2 string topics do not enforce valid states, source identity, timestamps, or data freshness.
- Dashboard JSON file exchange does not authenticate data or expose health checks for stale state.
- A future physical deployment would add risks from robot motion, people nearby, uneven terrain, communication loss, and incorrect site interpretation.

## Responsible development requirements

Before any real-world use, the project would need a documented hazard analysis, risk assessment, fail-safe behavior, independent emergency stop, human supervision, access control, operational boundaries, and testing under a qualified robotics safety process. The system should not make autonomous safety decisions about workers or replace required site procedures.

If future versions use cameras or other sensors in occupied work areas, the team should minimize collection, avoid identifying workers unless essential, define retention and access rules, and communicate what the system observes. Any model outputs should be presented with uncertainty and should not be treated as verified facts without human review.
