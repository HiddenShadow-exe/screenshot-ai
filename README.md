Screenshot AI takes a screenshot of your screen when a keybind is pressed, prompts an LLM to answer the question visible in the screenshot, then shows the answer in a tray icon. All this without anyone realizing you are using AI to answer the quesion.

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

# Screenshot AI v2
docs coming soon...
