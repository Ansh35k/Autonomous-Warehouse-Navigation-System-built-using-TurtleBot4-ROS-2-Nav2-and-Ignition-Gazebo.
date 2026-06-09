import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
from pyzbar.pyzbar import decode

class QRDecoderNode(Node):
    def __init__(self):
        super().__init__('qr_decoder_node')
        self.bridge = CvBridge()
        self.last_decoded = None

        self.sub = self.create_subscription(
            Image,
            '/oakd/rgb/preview/image_raw',  # corrected topic
            self.image_callback,
            10
        )
        self.pub = self.create_publisher(String, '/qr_code_detected', 10)
        self.get_logger().info('QR Decoder Node started')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        codes = decode(gray)

        for code in codes:
            data = code.data.decode('utf-8').strip()
            if data != self.last_decoded:
                self.last_decoded = data
                out = String()
                out.data = data
                self.pub.publish(out)
                self.get_logger().info(f'QR Detected: {data}')

def main(args=None):
    rclpy.init(args=args)
    node = QRDecoderNode()
    rclpy.spin(node)
    rclpy.shutdown()
