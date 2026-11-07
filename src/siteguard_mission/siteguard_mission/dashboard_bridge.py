
import json
import os
from pathlib import Path
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32

OUTPUT = Path(
    os.environ.get(
        "SITEGUARD_STATE_FILE",
        str(Path.home() / ".local/state/siteguard/dashboard_state.json")
    )
).expanduser()


class DashboardBridge(Node):

    def __init__(self):
        super().__init__("siteguard_dashboard_bridge")

        self.state = {
            "mission_state": "WAITING",
            "hazard_status": "UNKNOWN",
            "telemetry": {},
            "sim_position": 0.0,
            "updated": "Waiting for ROS 2",
            "events": []
        }

        self.create_subscription(
            String,
            "/siteguard/mission_state",
            lambda msg: self.update("mission_state", msg.data),
            10
        )

        self.create_subscription(
            String,
            "/siteguard/hazard_status",
            lambda msg: self.update("hazard_status", msg.data),
            10
        )

        self.create_subscription(
            String,
            "/siteguard/go2/telemetry",
            self.telemetry,
            10
        )

        self.create_subscription(
            Float32,
            "/siteguard/sim_position",
            self.sim_position,
            10
        )

        self.create_timer(0.5, self.save)

        self.get_logger().info(
            "Dashboard bridge: READ ONLY"
        )

    def update(self, key, value):
        previous = self.state.get(key)
        self.state[key] = value

        if previous != value:
            event = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": key.upper(),
                "value": value
            }

            self.state["events"].append(event)
            self.state["events"] = self.state["events"][-20:]

    def telemetry(self, msg):
        try:
            data = json.loads(msg.data)

            p = data.get("position", [0, 0, 0])
            v = data.get("velocity", [0, 0, 0])

            self.state["telemetry"] = {
                "x": round(p[0], 2),
                "y": round(p[1], 2),
                "velocity": round(
                    sum(n * n for n in v) ** 0.5, 2
                ),
                "body_height": data.get("body_height", 0),
                "mode": data.get("mode", 0)
            }

        except (ValueError, TypeError, IndexError):
            pass

    def sim_position(self, msg):
        self.state["sim_position"] = round(
            float(msg.data), 2
        )

    def save(self):
        self.state["updated"] = datetime.now().isoformat(
            timespec="seconds"
        )

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(self.state),
            encoding="utf-8"
        )


def main():
    rclpy.init()
    node = DashboardBridge()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
