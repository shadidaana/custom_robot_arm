# MoveIt 2 Cartesian Motion Demo

This package provides a simple demo for Cartesian motion planning with MoveIt 2 in ROS 2.

## Build and Run Process

### Step 1: Build the Package
```bash
cd ~/manipulator_ws
colcon build --symlink-install
# colcon build --packages-select moveit2_cartesian_demo
```

### Step 2: Source the Workspace
```bash
source install/setup.bash
```

### Step 3: Run the Demo
```bash
ros2 run moveit2_cartesian_demo simple_test
```

### File Structure

moveit2_cartesian_demo/
├── CMakeLists.txt          # Build configuration
├── package.xml            # Package metadata and dependencies
├── src/
│   └── simple_test.cpp    # Main executable source code
└── README.md             # This file


## Common Issues

### 1. `"Package not found" error`:  

Re-source your ROS 2 installation
```bash
source /opt/ros/humble/setup.bash
```
Then source your workspace
```bash
source ~/manipulator_ws/install/setup.bash
```

### 2. `"Executable not found" error`:
Rebuild the package
```bash
cd ~/manipulator_ws
colcon build --packages-select moveit2_cartesian_demo
source install/setup.bash
```

### 3. MoveIt connection errors
Ensure your robot simulation is running:
```bash
#ros2 launch your_robot_package robot_gazebo_launch.launch.py
```

## Useful Debug Commands

### Check if nodes are running
```bash
ros2 node list
```
### Check if topics are published
```bash
ros2 topic list
```
### Check joint states
```bash
ros2 topic echo /joint_states
```
### Check controller status
```bash
ros2 control list_controllers
```