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
