#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <geometry_msgs/msg/pose.hpp>
#include <vector>

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("cartesian_path_demo");
  node->set_parameter(rclcpp::Parameter("use_sim_time", true));
  
  // Multi-threaded executor (your fix)
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  std::thread([&executor]() { executor.spin(); }).detach();
  
  rclcpp::sleep_for(std::chrono::seconds(5));
  
  try {
    auto move_group = std::make_shared<moveit::planning_interface::MoveGroupInterface>(node, "arm");
    
    // Get current pose
    auto current_pose = move_group->getCurrentPose();
    std::cout << "Current position: x=" << current_pose.pose.position.x 
              << ", y=" << current_pose.pose.position.y 
              << ", z=" << current_pose.pose.position.z << std::endl;
    
    // Define waypoints for straight line motion
    std::vector<geometry_msgs::msg::Pose> waypoints;
    
    // Start from current position
    waypoints.push_back(current_pose.pose);
    
    // Create target pose (10cm straight in X direction)
    geometry_msgs::msg::Pose target_pose = current_pose.pose;
    target_pose.position.x += 0.5;  // 10cm in X
    
    // Add intermediate points for straight line
    int num_points = 10;  // Number of intermediate points
    for (int i = 1; i <= num_points; ++i) {
      geometry_msgs::msg::Pose intermediate_pose = current_pose.pose;
      intermediate_pose.position.x += (0.10 * i) / num_points;
      waypoints.push_back(intermediate_pose);
    }
    
    // Add final target
    waypoints.push_back(target_pose);
    
    // Compute Cartesian path
    moveit_msgs::msg::RobotTrajectory trajectory;
    const double eef_step = 0.01;  // Resolution (meters)
    const double jump_threshold = 0.0;  // Disable jump prevention
    
    double fraction = move_group->computeCartesianPath(waypoints, eef_step, jump_threshold, trajectory);
    
    std::cout << "Cartesian path completion: " << fraction * 100 << "%" << std::endl;
    
    if (fraction >= 0.9) {  // At least 90% achievable
      // Create and execute plan
      moveit::planning_interface::MoveGroupInterface::Plan plan;
      plan.trajectory_ = trajectory;
      
      std::cout << "Executing straight line motion..." << std::endl;
      move_group->execute(plan);
      std::cout << "Straight line motion completed!" << std::endl;
    } else {
      std::cout << "Cartesian path planning failed! Only " << fraction * 100 << "% achievable" << std::endl;
    }
    
  } catch (const std::exception& e) {
    std::cout << "Error: " << e.what() << std::endl;
  }
  
  rclcpp::shutdown();
  return 0;
}