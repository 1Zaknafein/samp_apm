# samp_apm

Python script for measuring APM during samp gameplay

## Usage

Run just like normal python script, using command prompt or fitting interpreter. Press F10 to start, and play as usual, but try to play at least few minutes to get more accurate results.
Hit F11 to end listening and get results. Two test result files will be created in the same directory as the script.

## Prerequisites 

Libraries pynput, numpy and matplotlib are required to run this script.


## How it works
Upon pressing the start key, the script will listen for specific keys used in SAMP gameplay; mainly WSAD, Q, E, C and spacebar keys, along with mouse clicks in order to increment a counter whenever such key was detected to be pressed. Every 5 seconds the number of registered keys is then added to a list of results, which will then be used to present the data.

As of current version
- Pressing ESC or opening chat ('T' key)  effectively pauses the counter to provide much more accurate results, as only measuring gameplay is desired.
- Pressing ESC while game is paused (in menu or typing) will unpause the counter, as well as hitting Enter to send the message in chat.
- Holding down a key is prevented from breaking the results, done by checking how much time has passed since the same key was pressed.

## Example results

#### run time = 0:02:58
#### key presses = 1416
#### average apm = 523.5
#### highest apm = 526
#### average actions per second = 8.7
#### highest actions per second = 11.8

![test_graph](https://user-images.githubusercontent.com/98032843/156214599-952d73b1-9b8e-4632-b1ec-a7a40600a8a1.png)


## Note
Technically it is a keylogger (as its listening for keyboard and mouse input), therefore it might be flagged by AV
