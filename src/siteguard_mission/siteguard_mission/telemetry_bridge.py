import json
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from unitree_sdk2py.core.channel import (
    ChannelFactoryInitialize,
    ChannelSubscriber
)
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_


class TelemetryBridge(Node):

    def __init__(self):
        super().__init__('siteguard_telemetry_bridge')

        self.publisher = self.create_publisher(
            String,
            '/siteguard/go2/telemetry',
            10
        )

        self.lock = threading.Lock()
        self.latest_state = None

        self.subscriber = ChannelSubscriber(
            'rt/sportmodestate',
            SportModeState_
        )

        self.subscriber.Init(self.state_callback, 10)

        self.timer = self.create_timer(
            0.5,
            self.publish_telemetry
        )

        self.get_logger().info(
            'SITEGUARD-AI read-only telemetry bridge started'
        )

    def state_callback(self, state):
        snapshot = {
            'position': list(state.position),
            'velocity': list(state.velocity),
            'body_height': float(state.body_height),
            'mode': int(state.mode),
            'error_code': int(state.error_code)
        }

        with self.lock:
            self.latest_state = snapshot

    def publish_telemetry(self):
        with self.lock:
            state = self.latest_state

        if state is None:
            return

        msg = String()
        msg.data = json.dumps(state)

        self.publisher.publish(msg)


def main(args=None):
    ChannelFactoryInitialize(1, 'lo')

    rclpy.init(args=args)
    node = TelemetryBridge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
