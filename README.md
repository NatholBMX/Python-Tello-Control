# Python-Tello-Control
Controlling the Tello drone with Python

Based on the works from [PyTello](https://bitbucket.org/PingguSoft/pytello)
and [TelloyPy](https://github.com/hanyazou/TelloPy)

## What can it currently do?
1. You can start and land the drone with Left CTRL and W respectively.

2. You can make the drone follow your face. Currently, only frontal face recognition
for one face is supported. Beware that it is heavily dependent on lighting conditions,
so it does not always work.

3. You can make the drone track your hand.


## Requirements
Install [TelloyPy](https://github.com/hanyazou/TelloPy) and get the neural network weights
for the hand tracking from 
[Convolutional Pose Machines Tensorflow](https://github.com/timctho/convolutional-pose-machines-tensorflow)

## Running the drone with face tracking

````python
python telloPyFacetracking.py
````


Beware that take off and landing has to be done manually.

## Demo for facetracking

![](https://github.com/NatholBMX/Python-Tello-Control/blob/development/images/Facetrack.gif "Face Tracking")

## Demo for handtracking

![](https://github.com/NatholBMX/Python-Tello-Control/blob/development/images/Jedi.gif "Jedi")