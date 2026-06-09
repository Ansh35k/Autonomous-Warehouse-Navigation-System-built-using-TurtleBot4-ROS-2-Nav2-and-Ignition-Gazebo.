import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math


QR_SIGN_LOCATIONS = {
    "RACK_A1":    {"x": -0.44, "y": -4.63},
    "RACK_A2":    {"x":  2.56, "y": -2.43},
    "RACK_B1":    {"x":  5.24, "y": -4.76},
    "RACK_B2":    {"x": -0.90, "y":  3.47},
    "DROPZONE_1": {"x":  0.50, "y":  0.50},
}
TRIGGER_DISTANCE = 0.8  # meters

class QRProximityTrigger(Node):
    def __init__(self):
        super().__init__('qr_proximity_trigger')
        self.triggered = set()  # avoid re-triggering

        self.sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(String, '/qr_code_detected', 10)
        self.get_logger().info('QR Proximity Trigger started')

    def odom_callback(self, msg):
        rx = msg.pose.pose.position.x
        ry = msg.pose.pose.position.y

        for name, pos in QR_SIGN_LOCATIONS.items():
            dist = math.sqrt((rx - pos['x'])**2 + (ry - pos['y'])**2)
            if dist < TRIGGER_DISTANCE and name not in self.triggered:
                self.triggered.add(name)
                out = String()
                out.data = name
                self.pub.publish(out)
                self.get_logger().info(f'QR triggered by proximity: {name}')

def main(args=None):
    rclpy.init(args=args)
    node = QRProximityTrigger()
    rclpy.spin(node)
    rclpy.shutdown()
