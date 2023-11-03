# Top-down-game

___NOTE: This game does not have automatic updates. You will need to download any new versions you want by yourself and transfer the "savedData.txt" and "save1.txt" files.___  
  
This is a prototype game. Currently, there is no way to initialize your username within the app. Take the following steps to manually initialize the "savedData.txt" before that is the case:
1. Add `Username: [username]`, where `[username]` is your username.
2. Add `Color: [color]`, where `[color]` is your preferred in-game color. The current colors are shown in the following list: "Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", and "White".
In the end, your "savedData.txt" file should take the following format (the Unicode symbol ⏎ has been added at the end of each line to clear confusion over whitespaces):
```
Username: Example⏎
Color: White
```
Run "main.py" to play the game, and run "server.py" to just launch a server. With "server.py", it will open a window; close the window to shut down the server.
