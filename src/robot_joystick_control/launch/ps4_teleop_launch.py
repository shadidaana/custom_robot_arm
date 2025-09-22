from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Joystick driver node
        Node(
            package="joy",
            executable="joy_node",
            name="joy_node",
            output="screen"
        ),

        # Your teleop node
        Node(
            package="robot_joystick_control",
            executable="ps4_teleop",
            name="ps4_teleop",
            output="screen"
        ),
    ])
