from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory
import os
import xacro

controllers_yaml = os.path.join(
    get_package_share_directory("industrial_robot_arm_moveit"),
    "config",
    "moveit_controllers.yaml"
)


def generate_launch_description():
    # Load MoveIt config
    moveit_config = (
        MoveItConfigsBuilder("Robotic", package_name="industrial_robot_arm_moveit")
        .to_moveit_configs()
    )

    # Robot State Publisher (publishes TF from URDF)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    # ros2_control Node (to manage controllers)
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            moveit_config.robot_description, 
            os.path.join(
                get_package_share_directory("industrial_robot_arm_moveit"),
                "config",
                "ros2_controllers.yaml"
            )
        ],
        output="screen",
    )

    # Spawner for joint_state_broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
        output="screen",
    )

    # Spawner for manipulator controller
    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # Spawner for gripper controller (added)
    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # MoveGroup node

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"joint_state_topic": "/joint_states"},
            {"moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager"},
            {"controller_names": ["arm_controller", "gripper_controller"]},
        ],
    )


#    move_group_node = Node(
#       package="moveit_ros_move_group",
#        executable="move_group",
#        output="screen",
#        parameters=[moveit_config.to_dict(), {"joint_state_topic": "/joint_states"}],
#    )

    # RViz2 with MoveIt config
    rviz_config_path = moveit_config.package_path / "config/moveit.rviz"
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", str(rviz_config_path)],
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    return LaunchDescription([
        robot_state_publisher,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        gripper_controller_spawner,   # <-- added here
        move_group_node,
        rviz_node,
    ])
