# Python-Tello-Control
Controlling the Tello drone with Python

Based on the works from (https://bitbucket.org/PingguSoft/pytello)

## Requirements
For running the drone with video stream [MPlayer](http://www.mplayerhq.hu/design7/news.html) is needed.

## Running the program with video output

```
python runWithVideostream.py
```

Starts the programm and directly outputs video stream to MPlayer.
You can then simply control the drone and view the video file.

## Running the drone with face tracking

```
python runWithFaceTracking.py
```

MPlayer is still used for generating the video, but every frame is saved as a picture
to the local drive. Image analysis then works on the PC, finds the first face and 
orders the drone to follow it. Currently only turning left/right and flying up/down is
supported for safety reasons.