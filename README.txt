Relevant Image Finder

Brandon Chastain
Danny Gonzalez
James Mullenbach


RUNNING THE APP YOURSELF
========================
THE EASY WAY:
------------------------
You can install our extension from the Chrome Store here: https://chrome.google.com/webstore/detail/relevant-image-finder/hkdncfacadljddbhlpahnogdlcbcjppe

You should now see a blue painting icon at the top-right of your Chrome window. (If you don't, click the three-bar menu and it should be there.) Click it to run the extension.
It should work right out of the box. It may be slow at the first attempt because the server takes several seconds to wake up.



THE HARD WAY (INSTALL THE EXTENSION FROM SOURCE):
------------------------
1. Open Chrome.
2. Go to the three-bar menu -> More Tools... -> Extensions.
3. Check the "Developer Mode" option.
4. Click "Load unpacked extension..."
5. Select the folder inside our project labeled "extension" and click OK.

You should now see a blue painting icon at the top-right of your Chrome window. (If you don't, click the three-bar menu and it should be there.) Click it to run the extension.
It should work right out of the box. It may be slow at the first attempt because the server takes several seconds to wake up.


This extension points to a web server which has our code, hosted at heroku.com. You can view the source in this folder.
You can even run the backend yourself, but it takes some configuration:

DEPENDENCIES
Most recent JDK
Python 2 (we used Python 2.7.10 and 2.7.11)
Pip

INSTALLATION
For the back end:
1. Unzip the folder, open up a command prompt and cd into the newly created folder.
2. From there, run the following command: "pip install -r requirements.txt"
    * This should install all the python libraries required to run the script.
    * You can cat requirements.txt to see what libraries this is using.
To set up the front end:
1. On line 1 of popup.js (in the extension folder), change the url to "http://localhost:5000/?text=" and reinstall the extension.
Your environment should be ready to run the script.

RUNNING THE SCRIPT
In a command prompt in the root of the folder, run "python main.py".

You may need to click "Allow" on a popup asking if it can run. After that, you
are running the back end script! Go on to use the chrome extension normally.
You should see that it uses your own machine as the server.
