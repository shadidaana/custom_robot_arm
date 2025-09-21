cmake_minimum_required(VERSION 3.8)
project(moveit2_cartesian_demo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(geometry_msgs REQUIRED)

# Add executable
    #What it does: Creates an executable program from your source code
    # simple_test: The name of your executable (what you'll run with ros2 run)
    # src/simple_test.cpp: The source file to compile

add_executable(simple_test
  src/simple_test.cpp
)

add_executable(cartesian_path
  src/cartesian_path.cpp
)

# Link dependencies
  # What it does: Links your executable to the required libraries
  # simple_test: The executable to link
  # The list: Packages to link against (headers + libraries)

ament_target_dependencies(simple_test
  rclcpp
  moveit_ros_planning_interface
  geometry_msgs
)

ament_target_dependencies(cartesian_path
  rclcpp
  moveit_ros_planning_interface
  geometry_msgs
)


# Install
  # What it does: Copies the built executable to the install directory
  # DESTINATION lib/${PROJECT_NAME}: Installs to install/moveit2_cartesian_demo/lib/moveit2_cartesian_demo/

install(TARGETS simple_test
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS cartesian_path
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
