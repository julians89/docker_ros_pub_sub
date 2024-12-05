# ------ Base Ubuntu image with ROS installed ------
FROM ubuntu:20.04 AS ros_image

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Minsk
RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install wget tzdata gnupg2 curl lsb-core vim bash \
    && apt-get clean

# Installing ROS-noetic
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
RUN curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | apt-key add -
#This can take 10 minutes ...
RUN apt update && apt install -y ros-noetic-desktop-full python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
RUN rosdep init && rosdep update
RUN echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc

# Intalling catkin & stuff
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu `lsb_release -sc` main" > /etc/apt/sources.list.d/ros-latest.list'
RUN wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
RUN apt-get update && apt-get install -y python3-catkin-tools software-properties-common