FROM ubuntu:20.04
MAINTAINER wjrals198
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
COPY ./program /home/
RUN apt-get install -y wget
RUN apt-get install -y build-essential cmake
#camke install

RUN apt-get install -y pkg-config && apt-get install -y unzip 
RUN apt-get install -y libjpeg-dev libtiff5-dev libpng-dev
RUN apt-get install -y ffmpeg libavcodec-dev libavformat-dev libswscale-dev libxvidcore-dev libx264-dev libxine2-dev
RUN apt-get install -y libv4l-dev v4l-utils
RUN apt-get install -y libgstreamer1.0-dev
RUN apt-get install -y libgstreamer-plugins-base1.0-dev
RUN apt-get install -y mesa-utils libgl1-mesa-dri libgtkgl2.0-dev libgtkglext1-dev
RUN apt-get install -y libatlas-base-dev gfortran libeigen3-dev
RUN apt-get install -y python3-dev python3-numpy

RUN apt-get install -y unzip && mkdir home/opencv
RUN cd /home/opencv
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip && unzip opencv.zip
RUN wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.4.0.zip && unzip opencv_contrib.zip
RUN cd opencv-4.4.0 && mkdir bulid && cd bulid && cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=OFF -D WITH_IPP=OFF -D WITH_1394=OFF -D BUILD_WITH_DEBUG_INFO=OFF -D BUILD_DOCS=OFF -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=OFF -D BUILD_PACKAGE=OFF -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D WITH_QT=OFF -D WITH_GTK=ON -D WITH_OPENGL=ON -D BUILD_opencv_python3=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.4.0/modules -D WITH_V4L=ON  -D WITH_FFMPEG=ON -D WITH_XINE=ON -D OPENCV_ENABLE_NONFREE=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D OPENCV_SKIP_PYTHON_LOADER=ON -D OPENCV_GENERATE_PKGCONFIG=ON ../ && make && make install

#opencv install
RUN apt-get install -y pip
RUN apt-get install -y libboost-all-dev && pip install dlib -vvv && pip3 install face_recognition

#speaker module
RUN pip install pydub && pip install gtts 
