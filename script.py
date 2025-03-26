import time
import keyboard
import pyautogui
import pyperclip
import os
import tempfile
import win32clipboard
import ctypes
from PIL import Image
import io
import sys
from PyQt5.QtWidgets import QApplication
import win32gui
import win32con
import win32console
import pygetwindow as gw

from screenshotoverlay import ScreenshotOverlay
from trayicon import TrayIcon
from user import get_window, get_hide
from ansi import ansi

def find_window(title_keyword):
    """Finds a window that contains a specific keyword in its title."""
    try:
        windows = gw.getAllTitles()  # Get all window titles
        for title in windows:
            if title_keyword in title:  # Check if the keyword is in the title
                return gw.getWindowsWithTitle(title)[0]  # Return the first match
        return None
    except ImportError:
        print("[ERROR] pygetwindow is not installed. Install it with: pip install pygetwindow")
        return None

def activate_window(window):
    """Activates the given window."""
    if window:
        window.activate()

def take_screenshot(filename):
    """Takes a screenshot and saves it to the given filename."""
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

def paste_image_and_prompt(prompt, mouse_pos):
    """Pastes the image into the Gemini window and adds the prompt."""
    try:
        pyautogui.click(x=mouse_pos[0], y=mouse_pos[1], clicks=1) #click on the input field.
        pyautogui.hotkey('ctrl', 'v') #paste image.
        time.sleep(2)
        pyperclip.copy(prompt)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v') #paste prompt
        time.sleep(0.5)
        pyautogui.press('enter') #send prompt

    except Exception as e:
        print(ansi.FAIL + f"[ERROR] Error pasting image/prompt: {e}" + ansi.ENDC)

def get_gemini_answer(scroll_area_pos, answer_text_pos):
    """Retrieves and parses the answer from the Gemini response using PyAutoGUI clicks."""
    try:
        activate_window(find_window(get_moodle_window_name())) # go back while we wait
        time.sleep(10)  # Wait for the response to load.
        activate_window(find_window("Gemini - Google Chrome"))

        # Click on the scrollarea to focus it
        pyautogui.click(x=scroll_area_pos[0], y=scroll_area_pos[1], clicks=3)
        time.sleep(0.5)

        # Scroll down by pressing the DOWN ARROW key multiple times
        for _ in range(4):  # You can adjust the range for more or fewer scrolls
            pyautogui.press('down')
            time.sleep(0.5)  # Small delay between presses

        # Click three times to select the whole answer
        pyautogui.click(x=answer_text_pos[0], y=answer_text_pos[1], clicks=3)
        time.sleep(1) #delay to allow selection.

        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1) #delay to allow copy.

        answer = pyperclip.paste()
        return answer.strip()

    except Exception as e:
        print(ansi.FAIL + f"Error getting Gemini answer: {e}" + ansi.ENDC)
        return "Error retrieving answer."


def get_moodle_window_name():
    import pygetwindow as gw
    for window in gw.getAllTitles():
        if len(window) > 60 and window.endswith("| BME GTK - Google Chrome"):
            return window

def send_image_to_clipboard(image_path):
    """Copies the image data to the clipboard (Windows only)."""
    image = Image.open(image_path)
    output = io.BytesIO()
    image.convert("RGB").save(output, "BMP") #BMP is the best format for windows clipboard.
    data = output.getvalue()[14:]  # BMP header offset.
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def process_question(overlay, trayicon, win, positions):
    """Main function to handle the question processing."""
    print(ansi.HEADER + "--------------------------------" + ansi.ENDC)

    try:
        browser_window = None
        if win == "Auto":
            browser_window = find_window(get_moodle_window_name())
        else:
            print(win)
            browser_window = find_window(win)

        if not browser_window:
            browser_window = find_window(get_moodle_window_name())

        gemini_window = find_window("Gemini - Google Chrome")

        if not browser_window or not gemini_window:
            print(ansi.FAIL + "[ERROR] Browser windows not found." + ansi.ENDC)
            print(ansi.OKBLUE + f"[INFO] Browser_window: {browser_window}" + ansi.ENDC)
            print(ansi.OKBLUE + f"[INFO] Gemini_window: {gemini_window}" + ansi.ENDC)
            print(ansi.OKBLUE + "[INFO] Make sure the browser windows are open and have the correct titles." + ansi.ENDC)
            app.quit()
            sys.exit()

        if not browser_window.isActive:
            print(ansi.FAIL + "[ERROR] Please make sure the browser window is active." + ansi.ENDC)
            return

        # Destructure mouse positions
        input_field_pos, scroll_area_pos, answer_text_pos = positions
        
        # Set loading icon in tray
        trayicon.set_loading()
        time.sleep(1)

        # Take screenshot & freeze screen
        activate_window(browser_window)
        time.sleep(0.5)
        temp_image_path = os.path.join(tempfile.gettempdir(), "question_screenshot.png")
        take_screenshot(temp_image_path)
        overlay.activate_signal.emit(temp_image_path)

        # Copy screenshot to clipboard
        send_image_to_clipboard(temp_image_path)

        # Switch to Gemini
        activate_window(gemini_window)
        time.sleep(0.5)

        # Pass data to Gemini
        prompt = "Solve this multiple choice question. Answer with as few words as possible. You aren't allowed to elaborate. The answer should not be longer than 50 characters. You are prohibited to write sentences."
        paste_image_and_prompt(prompt, input_field_pos)

        # Waits and gets answer from Gemini
        answer = get_gemini_answer(scroll_area_pos, answer_text_pos)

        # Switch back and unfreeze screen
        activate_window(browser_window)
        overlay.deactivate_signal.emit()

        if not answer:
            print(ansi.FAIL + "[ERROR] Empty answer received. Make sure not to move the mouse while the question is being processed." + ansi.ENDC)
            trayicon.display_answer("ERR", color="red")
            return

        if prompt in answer:
            print(ansi.FAIL + "[ERROR] Something went wrong. Make sure not to move the mouse while the question is being processed." + ansi.ENDC)
            trayicon.display_answer("ERR", color="red")
            return

        # Send notification
        trayicon.display_answer(answer)
        print(ansi.OKGREEN + f"[SUCCESS] Answer: {answer}" + ansi.ENDC)

        os.remove(temp_image_path) # Cleanup
    
    except Exception as e:
        print(ansi.FAIL + f"[ERROR] Error processing question: {e}" + ansi.ENDC)
        overlay.deactivate_signal.emit()
        sys.exit()

def get_mouse_positions():
    """Stores the mouse positions in a file."""
    file_path = "mouse_positions.txt"

    if os.path.exists(file_path):
        print(ansi.OKBLUE + "[INFO] Mouse positions file already exists. Using existing values." + ansi.ENDC)
        with open(file_path, "r") as file:
            lines = file.readlines()
            positions = [tuple(map(int, line.split(":")[1].strip().replace("(", "").replace(")", "").split(", "))) for line in lines]

    # Run mouse.py script to get the positions
    else:
        print(ansi.OKBLUE + "[INFO] Mouse positions file not found. Running mouse.py script to get the positions." + ansi.ENDC)
        os.system("py mouse.py")
        return get_mouse_positions()  # Call the function again to read the positions from the file

    return positions

def main(app, overlay):
    """Main function to set up the keybind."""
    console_hwnd = win32gui.GetForegroundWindow()
    trayicon = TrayIcon(app, console_hwnd)

    positions = get_mouse_positions()

    win = get_window()
    if win is None:
        print("Exiting...")
        app.quit()
        sys.exit()

    if win == "Auto":
        print(ansi.OKBLUE + f"[INFO] No window selected, defaulting to {get_moodle_window_name()}" + ansi.ENDC)

    hide = get_hide()

    trayicon.display_answer("RDY", color="green")
    print(ansi.OKGREEN + "[READY] Press Ctrl+Shift+Q to process the question." + ansi.ENDC)
    print(ansi.OKBLUE + "[INFO] Press Ctrl+Alt+Shift+C to quit." + ansi.ENDC)

    keyboard.add_hotkey("ctrl+shift+q", lambda: process_question(overlay, trayicon, win, positions))
    keyboard.add_hotkey("ctrl+alt+shift+c", lambda: app.quit())

    if hide:
        print(ansi.OKBLUE + "[INFO] Hiding the console window..." + ansi.ENDC)
        time.sleep(1)
        win32gui.ShowWindow(console_hwnd, win32con.SW_HIDE)  # Hide the window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = ScreenshotOverlay()
    main(app, overlay)
    sys.exit(app.exec_())          # Start the Qt event loop
