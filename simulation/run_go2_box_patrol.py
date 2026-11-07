#!/usr/bin/env python3
"""Run a scripted Go2 patrol in MuJoCo and detect orange boxes in camera pixels.

The official Go2 joint/mesh model is physics simulated. For this prototype,
the base follows a scripted kinematic path; this is not a locomotion controller.
The detector uses simple orange-color segmentation on the rendered camera image.
It is not a trained object detector and must not be treated as a safety sensor.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parent
SCENE = ROOT / "siteguard_scene.xml"
PATROL_SPEED = 0.30
PATROL_END_X = 9.5
SIM_STEP = 0.002
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
DETECTION_PIXEL_THRESHOLD = 120


@dataclass
class Detection:
    pixel_count: int
    bbox: tuple[int, int, int, int]


class RosBridge:
    """Optional ROS 2 bridge. Without --ros2 the demo runs standalone."""

    def __init__(self) -> None:
        import rclpy
        from rclpy.node import Node
        from std_msgs.msg import Float32, String

        self.rclpy = rclpy
        if not rclpy.ok():
            rclpy.init()

        class BridgeNode(Node):
            def __init__(self) -> None:
                super().__init__("siteguard_mujoco_box_patrol")
                self.hazard_pub = self.create_publisher(
                    String, "/siteguard/hazard_status", 10
                )
                self.position_pub = self.create_publisher(
                    Float32, "/siteguard/sim_position", 10
                )
                self.telemetry_pub = self.create_publisher(
                    String, "/siteguard/go2/telemetry", 10
                )

        self.node = BridgeNode()
        self.String = String
        self.Float32 = Float32
        self._last_publish = 0.0

    def publish(self, sim_time: float, x_position: float, detected: bool) -> None:
        if sim_time - self._last_publish < 0.25:
            self.rclpy.spin_once(self.node, timeout_sec=0.0)
            return

        hazard = self.String()
        hazard.data = "HAZARD_DETECTED" if detected else "NO_HAZARD"
        self.node.hazard_pub.publish(hazard)

        position = self.Float32()
        position.data = float(x_position)
        self.node.position_pub.publish(position)

        telemetry = self.String()
        telemetry.data = json.dumps(
            {
                "position": [float(x_position), 0.0, 0.27],
                "velocity": [0.0 if detected else PATROL_SPEED, 0.0, 0.0],
                "body_height": 0.27,
                "mode": 0,
                "error_code": 0,
                "source": "mujoco_scripted_patrol",
            }
        )
        self.node.telemetry_pub.publish(telemetry)
        self._last_publish = sim_time
        self.rclpy.spin_once(self.node, timeout_sec=0.0)

    def close(self) -> None:
        self.node.destroy_node()
        if self.rclpy.ok():
            self.rclpy.shutdown()


def detect_box(
    renderer: mujoco.Renderer,
    data: mujoco.MjData,
) -> Detection | None:
    """Find the orange target-color mask and return its image bounding box."""
    renderer.update_scene(data, camera="go2_front")
    image = renderer.render()
    red = image[:, :, 0].astype(np.int16)
    green = image[:, :, 1].astype(np.int16)
    blue = image[:, :, 2].astype(np.int16)
    mask = (red > 155) & (green > 35) & (green < 175) & (blue < 90) & (red > green + 45)
    rows, columns = np.nonzero(mask)
    if len(columns) < DETECTION_PIXEL_THRESHOLD:
        return None

    x_min, x_max = int(columns.min()), int(columns.max())
    y_min, y_max = int(rows.min()), int(rows.max())
    return Detection(
        pixel_count=int(len(columns)),
        bbox=(x_min, y_min, x_max - x_min + 1, y_max - y_min + 1),
    )


def hold_home_pose(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    home_qpos: np.ndarray,
) -> None:
    """Apply a modest PD hold torque to the 12 leg joints in the Go2 model."""
    for actuator_id in range(model.nu):
        joint_id = int(model.actuator_trnid[actuator_id, 0])
        qpos_id = int(model.jnt_qposadr[joint_id])
        dof_id = int(model.jnt_dofadr[joint_id])
        target = float(home_qpos[qpos_id])
        torque = 20.0 * (target - float(data.qpos[qpos_id])) - 0.7 * float(
            data.qvel[dof_id]
        )
        low, high = model.actuator_ctrlrange[actuator_id]
        data.ctrl[actuator_id] = float(np.clip(torque, low, high))


def set_scripted_base_pose(
    data: mujoco.MjData, home_qpos: np.ndarray, x: float, speed: float
) -> None:
    """Place the free base along the demo route; feet and joints remain dynamic."""
    data.qpos[:3] = (x, 0.0, float(home_qpos[2]))
    data.qpos[3:7] = (1.0, 0.0, 0.0, 0.0)
    data.qvel[:6] = 0.0
    data.qvel[0] = speed


def run(headless: bool, duration: float, use_ros2: bool) -> None:
    model = mujoco.MjModel.from_xml_path(str(SCENE))
    data = mujoco.MjData(model)
    model.opt.timestep = SIM_STEP

    home_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home")
    if home_id < 0:
        raise RuntimeError("The Go2 model has no 'home' keyframe")
    mujoco.mj_resetDataKeyframe(model, data, home_id)
    home_qpos = data.qpos.copy()
    bridge = RosBridge() if use_ros2 else None
    viewer = None
    if not headless:
        import mujoco.viewer

        viewer = mujoco.viewer.launch_passive(model, data)
    renderer = mujoco.Renderer(model, height=CAMERA_HEIGHT, width=CAMERA_WIDTH)

    detected: Detection | None = None
    detection_time: float | None = None
    detection_x: float | None = None
    next_camera_frame = 0.0
    start_wall = time.perf_counter()
    try:
        while data.time < duration and (viewer is None or viewer.is_running()):
            step_start = time.perf_counter()
            if detected is None:
                x = min(PATROL_SPEED * data.time, PATROL_END_X)
                set_scripted_base_pose(data, home_qpos, x, PATROL_SPEED)
            elif detection_x is not None:
                set_scripted_base_pose(data, home_qpos, detection_x, 0.0)

            hold_home_pose(model, data, home_qpos)
            mujoco.mj_step(model, data)
            mujoco.mj_forward(model, data)

            if detected is None:
                if data.time >= next_camera_frame:
                    detected = detect_box(renderer, data)
                    next_camera_frame = float(data.time) + 0.1
                    if detected is not None:
                        detection_time = float(data.time)
                        detection_x = float(data.qpos[0])
                        print(
                            "BOX FOUND IN FRONT CAMERA: "
                            f"pixels={detected.pixel_count} "
                            f"bbox={detected.bbox}; mission=SAFE_STOP"
                        )
                elif int(data.time * 10) != int((data.time - SIM_STEP) * 10):
                    print(
                        f"PATROL x={data.qpos[0]:.2f} m "
                        "| scanning Go2 camera image"
                    )

            if bridge is not None:
                bridge.publish(
                    sim_time=float(data.time),
                    x_position=float(data.qpos[0]),
                    detected=detected is not None,
                )

            if viewer is not None:
                viewer.sync()
            elif detected is not None and detection_time is not None:
                if data.time - detection_time >= 2.0:
                    break

            remaining = SIM_STEP - (time.perf_counter() - step_start)
            if remaining > 0:
                time.sleep(remaining)

        if detected is None:
            print("No orange box pixels were detected before timeout.")
        else:
            print("Simulation ended with the robot held at the first detected box.")
    finally:
        if viewer is not None:
            viewer.close()
        renderer.close()
        if bridge is not None:
            bridge.close()
        elapsed = time.perf_counter() - start_wall
        print(f"Simulation time={data.time:.1f} s, wall time={elapsed:.1f} s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--headless",
        action="store_true",
        help="run without a GUI and exit two simulation seconds after a detection",
    )
    parser.add_argument(
        "--duration", type=float, default=40.0, help="maximum simulated seconds"
    )
    parser.add_argument(
        "--ros2",
        action="store_true",
        help="publish hazard and position topics for the existing ROS 2 nodes",
    )
    args = parser.parse_args()
    run(headless=args.headless, duration=args.duration, use_ros2=args.ros2)


if __name__ == "__main__":
    main()
