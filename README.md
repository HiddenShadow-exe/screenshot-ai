# Prompt Engineering info
* Task number: own idea
* Name: Strumpf Dávid
* Docs: below
* AIs used while programming:
    - Gemini 2.5 Flash Preview
    - OpenAI ChatGPT
* Experiences:
    - It is not pleasent to work with python for UI backend and JS for frontend...
    - Regarding AI: it was really annoying that Gemini REALLY wants to display the whole code even after a small change was requested. For example, I asked it to add a new few-line short function that I wanted to use in one place. It returned the whole 400+ line code where I had to find where it put the new function. Even after explicitly telling it not to return the whole file, only show modifications, sometimes it still wouldn't behave. Not to mention that it always bloated the code with comments, which I really disliked. I guess Google made it this way to increase output token count thus being able to bill more to paid-tier users... I'm not sure.

## Prompts used
> [!NOTE]
> Recommend to skip this for now and return after reading about [what this project does](#screenshot-ai-v2).

### Initial prompt
From v1, I've already had some code that I also pasted for the AI to start with.
For example, the tray icon manager logic was almost complete.
```console
I wanna make an python script for Gemini API, here is my code to start with.
I wanna be able to attach an image whose content is a question.
I also wanna be able to attach (multiple) pdf files (both locally or from a URL) which content helps answer the question in the picture.
Also help me write an appropriate prompt based on the above info, make the AI answer as shortly as possible,
if it's a multiple choice question, anawer with only ABCD, if not, answer in as few words as possible, but always below 128 characters no matter what.
```
Note that I made the AI to do the Prompt Engineering for me. 😀
It had some problems implementing the latest Gemini API in python but after inserting the official docs from google, it started to look better. After small manual repair, the base was ready to go!

### Implementing GUI
After the core was working, I wanted a GUI to configure the parameters.
```console
I have these 3 files:
trayicon.py for managing the tray icon
gemini.py for handling AI communication
main.py the entry point

I want a 4th file that handles UI related tasks. I want a GUI to display a few things for the user:
* be able to upload the pdf files there (file upload from device/link)
* be able to choose from different AI models
* show the already used tokens all together and today (this needs some kind of "database", can be a simple json file)
* what currently gets printed to the console, should go in the GUI (so a way to display logs)
* after setting all these things up start listening for the keybinds. (during listening you cannot modify)
* be able to stop listening and tweak settings
* hide the GUI window, to make it appear, create a callback that can be called from the trayIcon button

Use a GUI framework of your choice, keep it simple but make it look modern. If you find it suitable, I'd love to try pywebview since I'm already pretty familiar with HTML, CSS
Do not modify my existing files, only tell me how to integrate it with the new system.
```
This yielded a pretty promising result. After debugging for a while to find out that the AI knows a previous version of pywebview, I got things working.

### Replace CSS with Tailwind
The previous prompt created an HTML and a CSS (and a JS) file additionally. I din't want to use CSS for this project, which got me to the next prompt.
I simply asked the AI to convert the HTML+CSS file into a single HTML file using Tailwind classes. It was able to do so flawlessly, first try. It is a more systematic task, the instruction is very clear, so I guess that's why it succedded first try.


# Screenshot AI v2
Screenshot AI takes a screenshot of your screen when a keybind is pressed, prompts an LLM to answer the question visible in the screenshot, then shows the answer in a tray icon. All this without anyone realizing you are using AI to answer the quesion.

## Setup
* You have to have Python installed on your system. The program was tested under Python 3.12.6
* Run this command to install dependencies:
  ```console
  pip install -r requirements.txt
  ```
* Start main.py

## Features & Usage
* You can extend the AI-s knowledge by uploading files
    - paste a link to a pdf and click "Add pdf"
    - click "Browse file" to upload from your device
* Choose the AI model to process the question
* Check out your daily and all-time token usage statistics
* See logs to know exactly what happens in the background
* Click start listening to listen for keybinds
* Optionally, you can hide the config window
* Finally, navigate to your question, and press `Ctrl+Shift+Q`

> [!NOTE]
> Some models are only available in the paid tier thus returning an error when called using free-tier API token

> [!IMPORTANT]
> When listening is in progress, settings cannot be modified

## Tray icon
When opening the program, a tray icon appears in the bottom right corner in your taskbar.

### Status indication
* Green background, displaying "RDY" means the program is running. It might not listen to keybinds though.
* Yellow background indicates loading.
* Red background, showing "ERR" means an error has occured. Check logs.
* Black/Gray background with some content, show the answer to the previous prompt.

> [!TIP]
> If you do not see the tray icon, click on the small upwards-pointing arrow, it might be there. In Windows Settings, you can pin the icon so it never gets hidden under the popup menu.

### Tray icon actions
By right clicking on the tray icon, you have two options:
* Show/Hide the config window
* Close the program

## Config window
![image](https://github.com/user-attachments/assets/30c8f79d-4d64-43e3-a29e-b8af016210fa)

# Screenshot AI v1
The original version of Screenshot AI didn't use an API to communicate with an LLM, it used a clever workaround to to interact with the GUI of the AI in a web browser. This was needed, since at the time v1 was made, there was no free unlimited-use API that could handle images, while the browser version of Gemini was capapble of doing so.

## Here is how it worked
1. It took a screenshot and saved it to the clipboard
2. Make the illusion of freezing the screen by creating a new window in full screen mode, setting its background to the screenshot. [*]
3. Switch to the other browser window running the Gemini GUI
4. Click in the input box and paste the screenshot and the prompt
5. Send the prompt and wait some time to finish processing
6. Copy the result and switch back to the original window, while closing the "freeze window"
7. Show result in the tray icon

[*] A key element here was to make this window click-transparent, meaning a mouse will simply "click through" the window. This way the full-screen window with the screenshot could be in forground, hiding the fact that something is happening in the background. One can imagine it like sticking a piece of paper on the monitor, so you see nothing but the paper, while having full control over the entire machine behind it.

## Usage
1. Open a browser window where the quesions were going to be from (only one tab)
2. Open another (separate) window where Gemini was open (and only that)
3. Start the script
4. First it prompts you to store some click info if not present
5. Follow the instructions where it makes you click in different parts of the gemini window to store mouse locations
6. Choose the the gemini window reference
7. Choose the question window reference
8. Setup is complete, you can use Ctrl+Shift+Q to start the process while having the question window in focus

## Ways things could go wrong
As one may see, it was a very fragile process, where even the smallest inperfection could destroy everything. Here are some examples of how things could go wrong:

### Retrieving answer from Gemini
After taking a screenshot, the program switches to the Gemini window, where it clicks in the input box (of which it knows the location of from prompting the user to click there during setup) and pastes the content. At this point if the click location was set up correctly, there is no problem so far. However, after we recieve the answer (of which by the way we don't know how long to wait for, so we wait fix 10s), the page would sometimes scroll indeterministicly, making the contents appear at a different locations then it would during the recording of mouse positions. This was meant to be handeled by scrolling as far down as possible by pressing the down-cursor a few times (programatically), however, it would not always work. The retriaval of the answer was solved by triple-clicking on the text, this selecting all of it, and pressing Ctrl+C. Sometimes due to unknown reasons it would not select anything, thus copying empty data to the clipboard.

### The window references not being correct
The program stored the title of the webpage where the questions are going to be from. If at any point the page title changed, and became different than was has been stored during setup, after retrieving the answer from Gemini, it would'n know where to switch back to, so it simply closed the "camouflage window", making Gemini fully visible, thus running the risk of getting caught cheating. Here is an example to better understand:
During setup, the HTML page's title was the following: `"Moodle | Start Quiz"`
It was stored when starting the program. After starting the quiz, the page title changed to `"Moodle | Quiz - Question 1"`

## Motivation for v2
Note that such an unexpected event (which was highly probable to occur) was nearly impossible to restore during live usage. In an exam environment, there was no way that the program could be restarted or reaparations could be made without raising suspicion of doing something else.
As this was a very unreliable and fragile system that could brake from a stronger breeze, a better solution was necessary.

## Achivement
Despite the previously described difficulties and huge instability, I was still able to use it to score 36/45 on a hungarian law quiz without learning a word.

## Goals for v2
With all the experiences from Screenshot AI v1, I had a handful of changes and expectations in mind:
1. using an API instead of the unreliable Alt+Tab solution would eliminate 99% of the weeknesses from v1, while aslo bring tons of advantages:
    - no need to switch windows and "fake-freeze" the screen, thus having full control while processing
    - the answer can we displayed whenever the LLM responds, eliminating the fix wait
    - no need to promt the user to provide (maybe incorrect) mouse positions making the program more user-friendly
2. since the AI did not score perticularly high on the test quiz, some kind of system would be nice to pass info about the topic to the AI, making it capable of scanning it, and answering more precizely
3. tracking the token usage to avoid unexpected error responses

With all theese in mind, Screenshot AI v2 was born...
