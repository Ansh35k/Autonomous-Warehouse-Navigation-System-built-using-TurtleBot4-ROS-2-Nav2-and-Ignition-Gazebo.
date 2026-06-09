import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math

QR_COORDINATE_MAP = {
    "RACK_A1":    {"x": 0.5, "y": 0.5, "yaw": 0.0},
    "RACK_A2":    {"x": 0.5, "y": 0.5, "yaw": 0.0},
    "RACK_B1":    {"x": 0.5, "y": 0.5, "yaw": 0.0},
    "RACK_B2":    {"x": 0.5, "y": 0.5, "yaw": 0.0},
    "DROPZONE_1": None,
}


def yaw_to_quaternion(yaw):
    return (0.0, 0.0, math.sin(yaw / 2), math.cos(yaw / 2))


class TaskManagerNode(Node):
    def __init__(self):
        super().__init__('task_manager_node')

        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.task_queue = []
        self.is_navigating = False

        self.sub = self.create_subscription(
            String,
            '/qr_code_detected',
            self.qr_callback,
            10
        )

        self.get_logger().info('Task Manager Node started')

    def qr_callback(self, msg):
        location_id = msg.data

        if location_id not in QR_COORDINATE_MAP:
            self.get_logger().warn(f'Unknown QR code: {location_id}')
            return

        if QR_COORDINATE_MAP[location_id] is None:
            self.get_logger().info('Reached DROPZONE - task complete, waiting for next pickup')
            return

        self.get_logger().info(f'Queueing goal: {location_id} -> DROPZONE')
        self.task_queue.append(location_id)

        if not self.is_navigating:
            self.dispatch_next()

    def dispatch_next(self):
        if not self.task_queue:
            self.is_navigating = False
            self.get_logger().info('All tasks complete')
            return

        self.is_navigating = True
        location_id = self.task_queue.pop(0)
        coords = QR_COORDINATE_MAP[location_id]

        self.get_logger().info(f'Navigating to {location_id} at {coords}')

        goal_msg = NavigateToPose.Goal()
        pose = PoseStamped()

        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = coords['x']
        pose.pose.position.y = coords['y']
        pose.pose.position.z = 0.0

        qx, qy, qz, qw = yaw_to_quaternion(coords['yaw'])
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        goal_msg.pose = pose

        self.get_logger().info('Waiting for Nav2 action server...')
        self.action_client.wait_for_server()

        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Distance remaining: {feedback.distance_remaining:.2f}m',
            throttle_duration_sec=2.0
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by Nav2')
            self.is_navigating = False
            self.dispatch_next()
            return

        self.get_logger().info('Goal accepted by Nav2')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        result = future.result()

        if result.status == 4:  # SUCCEEDED
            self.get_logger().info('Goal reached successfully')
        else:
            self.get_logger().warn(f'Goal failed with status: {result.status}')

        self.is_navigating = False
        self.dispatch_next()


def main(args=None):
    rclpy.init(args=args)
    node = TaskManagerNode()
    rclpy.spin(node)
    rclpy.shutdown()
