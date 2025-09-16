from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get package share directory
    pkg_share = get_package_share_directory('manipulator_3dof')
    xacro_file = os.path.join(pkg_share, 'urdf', 'manipulator_3dof.urdf.xacro')

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': Command(['xacro ', xacro_file])}]
    )

    # Joint State Publisher GUI node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # RViz node (use your saved RViz config or default)
    rviz_config_file = os.path.join(pkg_share, 'config', 'manipulator_3dof.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else []
    )

    # Launch all nodes
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])

