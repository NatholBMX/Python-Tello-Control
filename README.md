# Python-Tello-Control
Controlling the Tello drone with Python, making it as autonomous as possible.

Based on the works from and [TelloyPy](https://github.com/hanyazou/TelloPy) as a framework
for the Tello drone.

## What can it currently do?
1. You can start and land the drone with Left CTRL and W respectively.
Beware that for this to work, the Pygame Window has to be in the foreground (sorry for this hack).

2. You can make the drone follow your face. Currently, only frontal face recognition
for one face is supported. Beware that it is heavily dependent on lighting conditions,
so it does not always work.

3. You can make the drone track your hand. This depends heavily on GPU support,
so it might not work well with weak GPUs.


## Requirements
Install [TelloyPy](https://github.com/hanyazou/TelloPy) and get the neural network weights
for the hand tracking from 
[Convolutional Pose Machines Tensorflow](https://github.com/timctho/convolutional-pose-machines-tensorflow).

Since we use hand tracking, download this model: [Hand tracking weights](https://drive.google.com/file/d/1gOwBY5puCusYPCQaPcEUMmQtPnGHCPyl/view)

The weights must be saved in this folder location:
````commandline
cpm/models/weights/
````

## Running the drone with face tracking

````python
python telloPyFacetracking.py
````

## Running the drone with hand tracking

````python
python telloPyHandCPM.py
````


Beware that for both variants take off and landing has to be done manually.

## Demo for facetracking

![](https://github.com/NatholBMX/Python-Tello-Control/blob/development/images/Facetrack.gif "Face Tracking")

## Demo for handtracking

![](https://github.com/NatholBMX/Python-Tello-Control/blob/development/images/Jedi.gif "Jedi")