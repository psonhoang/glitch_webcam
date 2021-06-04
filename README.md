# About
A live webcam that glitches as you speak. The intensity of the glitch is dependent upon your pitch and volume input!

This was made for my UChicago's Media Arts Design & Practice - Spring 2021 final project!

## How it works
The project captures your webcam stream and serves it on your localhost:5000 endpoint with **opencv-python** and **flask**.

It detects your microphone input and analyzes its pitch and volume with **aubio**. The pitch and volume serve as heuristic for determining the intensity of the glitch.

When microphone input is detected, the frame at the time the input is detected will be saved as a JPEG image in order for **glitch_this** to glitch the image, which then save the *glitched* image object as a JPEG that will be used to generate our output video stream.

There is also a 50/50 chance that a bitwise-not filter will be applied to the frame before it is glitched - if it is deemed as glitch-worthy (glitch intensity > 0.1).

## Requirements
- python (python3 if you're on a Mac)

## Usage
If you're on Mac and have both python and python3, please use python3 and pip3
```bash
python -m venv virtualenv
source virtualenv/bin/activate
pip install -r requirements.txt
python run app.py
```