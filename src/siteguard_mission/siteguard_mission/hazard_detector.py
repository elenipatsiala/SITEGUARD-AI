import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HazardDetector(Node):

    def __init__(self):
        super().__init__('siteguard_hazard_detector')

        self.publisher = self.create_publisher(
            String,
            '/siteguard/hazard_status',
            10
        )

        self.elapsed_time = 0

        self.timer = self.create_timer(
            2.0,
            self.publish_hazard_status
        )

        self.get_logger().info(
            'SITEGUARD-AI Hazard Detector started'
        )

    def publish_hazard_status(self):

        self.elapsed_time = (self.elapsed_time + 2) % 30
        if 10 <= self.elapsed_time < 20:
            status = 'HAZARD_DETECTED'
        else:
            status = 'NO_HAZARD'

        msg = String()
        msg.data = status

        self.publisher.publish(msg)

        self.get_logger().info(
            f'Hazard status: {status}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = HazardDetector()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
