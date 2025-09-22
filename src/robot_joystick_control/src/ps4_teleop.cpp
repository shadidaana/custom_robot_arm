#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

#include <vector>

#define REVOLUTE_2_UPPER_LIMIT 0.698132
#define REVOLUTE_2_LOWER_LIMIT -3.141593
#define REVOLUTE_3_UPPER_LIMIT 0.349066
#define REVOLUTE_3_LOWER_LIMIT -2.443461
#define REVOLUTE_5_UPPER_LIMIT 1.9
#define REVOLUTE_5_LOWER_LIMIT -1.9


// #define CONSTRAIN(val, min_val, max_val) ((val) < (min_val) ? (min_val) : ((val) > (max_val) ? (max_val) : (val)))
constexpr double constrain(double val, double min_val, double max_val) {
    return (val < min_val) ? min_val : (val > max_val ? max_val : val);
}

class PS4Teleop : public rclcpp::Node {
public:
    PS4Teleop() : Node("ps4_teleop") {
        joy_sub_ = this->create_subscription<sensor_msgs::msg::Joy>(
            "/joy", 10, std::bind(&PS4Teleop::joy_callback, this, std::placeholders::_1)
        );

        // Subscribe to joint states
        joint_state_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10, std::bind(&PS4Teleop::joint_state_callback, this, std::placeholders::_1));

        traj_pub_ = this->create_publisher<trajectory_msgs::msg::JointTrajectory>(
            "/arm_trajectory_controller/joint_trajectory", 10
        );
    }

private:
    std::vector<double> current_positions = {0, 0, 0, 0, 0, 0};

    void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg) {
        // Update our internal joint positions from robot feedback
        for (size_t i = 0; i < msg->name.size(); i++) {
            for (size_t j = 0; j < current_positions.size(); j++) {
                if (msg->name[i] == joint_names_[j]) {
                    current_positions[j] = msg->position[i];
                }
            }
        }

        // RCLCPP_INFO(this->get_logger(),
        // "Current Joints: [%.3f, %.3f, %.3f, %.3f, %.3f, %.3f]",
        // current_positions[0],
        // current_positions[1],
        // current_positions[2],
        // current_positions[3],
        // current_positions[4],
        // current_positions[5]);

    }
    void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg) {
        trajectory_msgs::msg::JointTrajectory traj;
        traj.joint_names = joint_names_;
        trajectory_msgs::msg::JointTrajectoryPoint point;

        double step = 0.4;  // radians per callback tick

        // Update positions incrementally

        current_positions[0] += msg->axes[1] * step; // left stick vertical
        current_positions[1] = constrain(current_positions[1] + msg->axes[0] * step, REVOLUTE_2_LOWER_LIMIT, REVOLUTE_2_UPPER_LIMIT);// left stick horizontal
        current_positions[2] = constrain(current_positions[2] + msg->axes[3] * step, REVOLUTE_3_LOWER_LIMIT, REVOLUTE_3_UPPER_LIMIT);// right stick horizontal
        // current_positions[3] += msg->axes[2] * step; // right stick vertical
        current_positions[3] = current_positions[3] + msg->buttons[0] * step - msg->buttons[2] * step; // up-down 
        current_positions[4] = constrain(current_positions[4] + msg->buttons[4] * step - msg->buttons[5] * step, REVOLUTE_5_LOWER_LIMIT, REVOLUTE_5_UPPER_LIMIT);// right stick vertical
        current_positions[5] += msg->buttons[6] * step - msg->buttons[7] * step; // L2/R2 buttons

        point.positions = current_positions;
        
        point.time_from_start = rclcpp::Duration::from_seconds(0.5);
        traj.points.push_back(point);
        traj_pub_->publish(traj);
    }

    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_sub_;
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
    rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr traj_pub_;

    const std::vector<std::string> joint_names_ = {
        "revolute_1","revolute_2","revolute_3","revolute_4","revolute_5","revolute_6"
    };

};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<PS4Teleop>());
    rclcpp::shutdown();
    return 0;
}
