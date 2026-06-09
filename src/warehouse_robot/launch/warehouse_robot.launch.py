from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='warehouse_robot',
            executable='qr_decoder',
            name='qr_decoder_node',
            output='screen',
        ),
        Node(
            package='warehouse_robot',
            executable='task_manager',
            name='task_manager_node',
            output='screen',
        ),
        Node(
            package='warehouse_robot',
            executable='qr_proximity_trigger',
            name='qr_proximity_trigger_node',
            output='screen',
        ),
    ])
