import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MissionManager(Node):

    def __init__(self):
        super().__init__('siteguard_mission_manager')

        self.mission_state = 'PATROL'

        self.publisher = self.create_publisher(
            String,
            '/siteguard/mission_state',
            10
        )

        self.subscription = self.create_subscription(
            String,
            '/siteguard/hazard_status',
            self.hazard_callback,
            10
        )

        self.timer = self.create_timer(
            2.0,
            self.publish_mission_state
        )

        self.get_logger().info(
            'SITEGUARD-AI Mission Manager started'
        )

    def hazard_callback(self, msg):

        if msg.data == 'HAZARD_DETECTED':
            if self.mission_state != 'SAFE_STOP':
                self.mission_state = 'SAFE_STOP'
                self.get_logger().warning(
                    'HAZARD DETECTED - SAFE STOP ACTIVATED'
                )

        elif msg.data == 'NO_HAZARD':
            if self.mission_state != 'PATROL':
                self.mission_state = 'PATROL'
                self.get_logger().info(
                    'Hazard cleared - PATROL RESUMED'
                )

    def publish_mission_state(self):
        msg = String()
        msg.data = self.mission_state

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Mission state: {self.mission_state}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = MissionManager()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
