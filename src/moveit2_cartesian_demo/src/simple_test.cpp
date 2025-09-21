#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv); //Initializes ROS 2 framework

  rclcpp::NodeOptions options;
  options.parameter_overrides(
      {rclcpp::Parameter("use_sim_time", true)} //Tells ROS to use simulation time instead of real-world time
  );

  auto node = rclcpp::Node::make_shared("simple_test", options); //Creates a node named "simple_test"

    // Create a multi-threaded executor and add your node 
    // If it is not added then the followig error is thrown: 
    // [moveit ros.current_state monitor]: Didn't receive robot state...

    std::cout << "Creating a multi-threaded executor..." << std::endl;
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);
    std::thread([&executor]() { executor.spin(); }).detach();

    // // Wait for clock to be available
    // std::cout << "Waiting for simulation clock..." << std::endl;
    // rclcpp::sleep_for(std::chrono::seconds(3));

    // // Wait for joint states to be published
    // std::cout << "Waiting for joint states..." << std::endl;
    // rclcpp::sleep_for(std::chrono::seconds(5)); // Gives time for other ROS nodes to start up (MoveIt, Gazebo, controllers)
    
  try {
    // For the main arm
    auto move_group = std::make_shared<moveit::planning_interface::MoveGroupInterface>(node, "arm"); //Creates MoveIt interface for planning group named "arm" 
    //"arm" should match your MoveIt configuration

    // For the gripper (if needed)
    auto gripper_group = std::make_shared<moveit::planning_interface::MoveGroupInterface>(node, "gripper");

    std::cout << "MoveGroupInterface created successfully!" << std::endl;
    
    // Add this after creating move_group
    // move_group->startStateMonitor(10.0);  // Increase to 10 seconds
    // Additional wait for MoveIt to fully initialize
    // rclcpp::sleep_for(std::chrono::seconds(2));

    std::cout << "Trying to get current robot state!" << std::endl;

    // Try to get current state
    if (move_group->getCurrentState()) { //Checks if MoveIt can access robot joint states
      std::cout << "Robot state is available!" << std::endl;
      auto pose = move_group->getCurrentPose(); //: Gets the end-effector's current position
      std::cout << "Current position: x=" << pose.pose.position.x 
                << ", y=" << pose.pose.position.y 
                << ", z=" << pose.pose.position.z << std::endl;
    } else {
      std::cout << "Robot state is NOT available" << std::endl;
    }
    

    auto current_pose = move_group->getCurrentPose();
    // 1. Set a target pose
    geometry_msgs::msg::Pose target_pose = current_pose.pose;
    target_pose.position.x = 0.2;
    target_pose.position.y = 0.3;
    target_pose.position.z = .5;
    // target_pose.orientation.w = 1.0;

    // target_pose.position.x += 0.1;  // Only 5cm movement
    // target_pose.position.y += 0.1;  // Only 5cm movement
    // target_pose.position.z -= 0.1;  // Only 5cm movement

    // 2. Set the target
    move_group->setPoseTarget(target_pose);

    // 3. Plan the motion
    moveit::planning_interface::MoveGroupInterface::Plan plan;

    int attempts = 0;

    while (attempts < 3) {
        auto result = move_group->plan(plan);
        if(result == moveit::core::MoveItErrorCode::SUCCESS) {
            std::cout << "Planning successful! Executing movement..." << std::endl;
            move_group->execute(plan);
            break;
        }
        attempts++;
        // Try different planner or parameters
        move_group->setPlannerId(attempts == 1 ? "RRTConnect" : "RRTstar");
    }

    if (attempts>= 3){
        std::cout << "Planning failed!" << std::endl;
    }



  } catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
  }
  
  rclcpp::shutdown();
  return 0;
}