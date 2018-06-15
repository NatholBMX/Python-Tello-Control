# Python-Tello-Control
Controlling the Tello drone with Python

Based on the works from (https://bitbucket.org/PingguSoft/pytello)

## What can it currently do?
1. You are able to controll the drone with your PC's keyboard and get a video stream
from the drone to view it live on Desktop.

2. You can make the drone follow your face. Currently, only frontal face recognition
for one face is supported. Beware that it is heavily dependent on lighting conditions,
so it does not always work.


## Requirements
For running the drone with video stream [MPlayer](http://www.mplayerhq.hu/design7/news.html)
 is needed. This code is currently still hacky, so you need some disk space for temporarly
 saving pictures for later image analysis.

## Running the program with video output and manual keyboard control

```
python runWithVideostream.py
```

Starts the programm and directly outputs video stream to MPlayer.
You can then simply control the drone with your keyboard and view the video file.

## Running the drone with face tracking

```
python runWithFaceTracking.py
```

MPlayer is still used for generating the video, but every frame is saved as a picture
to the local drive. Image analysis then works on the PC, finds the first face and 
orders the drone to follow it. The drone follows your face when it is detected.

Currently, following tracking functions are implemented:
1. Turning the drone around the yaw axis to follow the face
2. Adjusting height to follow the face
3. Keeping constant distance from the face

Beware that take off and landing has to be done manually.