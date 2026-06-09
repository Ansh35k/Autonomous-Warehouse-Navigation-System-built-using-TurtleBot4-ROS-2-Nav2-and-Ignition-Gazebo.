# Autonomous Warehouse Navigation System

## Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install ros-humble-turtlebot4-*
sudo apt install ros-humble-nav2-bringup
sudo apt install python3-colcon-common-extensions
sudo apt install python3-opencv python3-pyzbar
```

---

## Step 2: Build Workspace

```bash
cd warehouse_ws
colcon build
source install/setup.bash
```

---

## Step 3: Run the System

### Terminal 1 (Simulation)

```bash
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py model:=lite world:=depot
```

### Terminal 2 (Localization + Nav2)

```bash
ros2 launch turtlebot4_navigation localization.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/depot.yaml \
  use_sim_time:=true &
sleep 20 && ros2 launch turtlebot4_navigation nav2.launch.py use_sim_time:=true
```

### Terminal 3 (RViz)

```bash
ros2 launch turtlebot4_viz view_robot.launch.py
```

> **MAKE SURE to set 2D Pose Estimate upwards**

### Terminal 4 (Warehouse Robot Nodes)

```bash
ros2 launch warehouse_robot warehouse_robot.launch.py
```

### Terminal 5 (Monitor QR Detections)

```bash
ros2 topic echo /qr_code_detected
```
