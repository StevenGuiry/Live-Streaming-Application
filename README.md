# Live Detect - Live Streaming Application

Before launching the application install the following libraries needed to run the application. 

Pip installs
 
```
pip install requirements.txt
```

To Launch
```
python ./webstreaming.py
```

It will launch a web page in your browser displaying the live stream from your default webcam. If you want to change the capture device alter line 28 of webstreaming.py file.

Features include:

- Email notifications sent to contacts when stream goes live
- Detects motion on the live stream
- Stores each stream locally for backup and to cloud storage
- Timestamp on each frame

- Motion detection computed by converting frame to grayscale and smoothening before converting each pixel to white/balck depending on if motion is detected and finally drawing rectangle on output frame where motion is found. 

<img src="https://user-images.githubusercontent.com/46968144/144079121-0bb62a9e-581f-4a78-919e-628b206c5a68.png" width="300" height="300"> <img src="https://user-images.githubusercontent.com/46968144/144079133-30b9de57-cc16-4c25-be01-7db01983783b.png" width="300" height="300"> <img src="https://user-images.githubusercontent.com/46968144/144079154-314a1b74-4ef3-4f92-9af5-13c07d6cc362.png" width="300" height="300">


- HTML/CSS implemented to style the web page
![image](https://user-images.githubusercontent.com/46968144/144081550-99a90955-e452-4ac4-9735-972f63ace1a2.png)



