from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription,RegisterEventHandler
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessStart
from launch.event_handlers import OnProcessExit
from launch.events import TimerEvent 
from launch.actions import TimerAction
from ament_index_python.packages import get_package_share_directory
import os
import xacro 
from moveit_configs_utils import MoveItConfigsBuilder
from launch.events import TimerEvent 
from launch.actions import TimerAction


import yaml


def generate_launch_description():
    ld =LaunchDescription()
    robot_description_file = os.path.join(
        get_package_share_directory('industrial_robot_arm_moveit'),'config','Robotic.urdf.xacro'
    )
    joint_controllers_file = os.path.join(
        get_package_share_directory('industrial_robot_arm_moveit'),'config','ros2_controllers.yaml'
    )
    gazebo_launch_file = os.path.join(
        get_package_share_directory('gazebo_ros'),'launch','gazebo.launch.py'
    )

    world_file = os.path.join(
        get_package_share_directory('gazebo_ros'),'worlds','empty.world'
    )


    # # Generate URDF from xacro
    robot_description = Command(["xacro ", robot_description_file])
    
    # MoveIt configs (robot_description now comes from xacro above)
    moveit_config = (
        MoveItConfigsBuilder("Robotic",package_name="industrial_robot_arm_moveit")
        .planning_pipelines(pipelines=["ompl", "chomp", "pilz_industrial_motion_planner"])
        .robot_description(file_path="config/Robotic.urdf.xacro")
        .robot_description_semantic(file_path="config/Robotic.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .to_moveit_configs()
    )

    x_arg = DeclareLaunchArgument('x', default_value='0', description='X position of the robot')
    y_arg = DeclareLaunchArgument('y', default_value='0', description='Y position of the robot')
    z_arg = DeclareLaunchArgument('z', default_value='0', description='Z position of the robot')


    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
        launch_arguments={
            'use_sim_time':'true',
            'debug': 'false',
            'gui':'true',
            'paused': 'true', 
            'world': world_file
        }.items()
    )

    # RViz2
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
            # moveit_config.robot_description,
            robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics,
        ],
    )


    # Spawn robot into Gazebo from topic /robot_description
    spawn_robot =Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=[
                "-entity", "Robotic",
                "-topic", "robot_description",
                "-x",LaunchConfiguration('x'),
                "-y",LaunchConfiguration('y'),
                "-z",LaunchConfiguration('z')
            ],
            output="screen"
        )


    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description_file,
            # {"robot_description": robot_description},
            # moveit_config.robot_description,
            joint_controllers_file
        ],
        output="both",
        remappings=[
            ("~/robot_description", "/robot_description")
        ],
    )


    # Robot State Publisher (publishes TF from URDF)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        # parameters=[moveit_config.robot_description],
        parameters=[{"robot_description": robot_description}],
        # parameters=[robot_description],
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

    use_sim_time={"use_sim_time":True}
    config_dict = moveit_config.to_dict()
    config_dict.update(use_sim_time)


    # MoveGroup node

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[config_dict],
        arguments=["--ros-arg","--log-level","info"],
    )

    delay_joint_state_broadcaster = RegisterEventHandler(
        OnProcessStart(
            target_action=ros2_control_node,
            on_start=[joint_state_broadcaster_spawner],
        )
    )

    delay_arm_controller = RegisterEventHandler(
        OnProcessStart(
            target_action=joint_state_broadcaster_spawner,
            on_start=[arm_controller_spawner],
        )
    )

    delay_gripper_controller = RegisterEventHandler(
        OnProcessStart(
            target_action=joint_state_broadcaster_spawner,
            on_start=[gripper_controller_spawner],
        )
    )

    delay_rviz_node = RegisterEventHandler(
        OnProcessStart(
            target_action=robot_state_publisher,
            on_start=[rviz_node],
        )
    )

    delay_ros2_control = RegisterEventHandler(
    OnProcessStart(
        target_action=robot_state_publisher,
        on_start=[ros2_control_node],
    )
)

    # Add this debug code before creating the node
    print("=== DEBUG INFO ===")
    print(f"robot_description type: {type(moveit_config.robot_description)}")
    print(f"controllers_yaml path: {joint_controllers_file}")
    print(f"controllers_yaml exists: {os.path.exists(joint_controllers_file)}")

    # Check if it's a file path or content
    if isinstance(moveit_config.robot_description, str):
        print(f"robot_description is a file path, exists: {os.path.exists(moveit_config.robot_description)}")
    else:
        print("robot_description is a dictionary")

    print("=== DEBUG INFO2 ===")
    # Debug what's in the robot_description
    print("Keys in robot_description:", moveit_config.robot_description.keys())
    if 'robot_description' in moveit_config.robot_description:
        print("robot_description key exists")
    else:
        print("robot_description key does not exist - showing all keys:")
        for key in moveit_config.robot_description.keys():
            print(f"  {key}: {type(moveit_config.robot_description[key])}")



    ld.add_action(x_arg)
    ld.add_action(y_arg)
    ld.add_action(z_arg)
    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(delay_ros2_control)
    ld.add_action(spawn_robot)
    ld.add_action(move_group_node)
    ld.add_action(delay_joint_state_broadcaster)
    ld.add_action(delay_arm_controller)
    ld.add_action(delay_gripper_controller)
    ld.add_action(delay_rviz_node)

    return ld
