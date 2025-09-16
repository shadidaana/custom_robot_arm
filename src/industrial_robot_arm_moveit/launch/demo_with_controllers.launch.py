import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("Robotic",package_name="industrial_robot_arm_moveit")
        .planning_pipelines(pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"])
        .robot_description(file_path="config/Robotic.urdf.xacro")
        .robot_description_semantic(file_path="config/Robotic.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    # ros2_control using FakeSystem as hardware
    ros2_controllers_path = os.path.join(
        get_package_share_directory("industrial_robot_arm_moveit"),
        "config",
        "ros2_controllers.yaml",
    )
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[moveit_config.robot_description, ros2_controllers_path],
        output="both",
    )

    # Spawner for joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # Spawner for manipulator controller
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_trajectory_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # Spawner for gripper controller (added)
    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_action_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # MoveGroup node

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
        arguments=["--ros-arg","--log-level","info"],
    )

    # RViz2 with MoveIt config
    rviz_config_path = os.path.join(
        get_package_share_directory("industrial_robot_arm_moveit"),
        "config",
        "moveit.rviz",
    )


    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", str(rviz_config_path)],
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
        ],
    )

    # Robot State Publisher (publishes TF from URDF)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )



    return LaunchDescription([
        ros2_control_node,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        gripper_controller_spawner,
        robot_state_publisher,
        move_group_node,
        rviz_node,
    ])