from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog, yes_no_dialog, input_dialog
import pygetwindow as gw

def get_window():
    # List of options to choose from
    options = set()

    for window in gw.getAllTitles():
        if window != "" and "- Google Chrome" in window and window != "Gemini - Google Chrome":
            options.add(window)

    # Creating a button dialog
    result = radiolist_dialog(
        title="Choose window",
        text="Please choose the window to take screenshots from!",
        values=[("Auto", "Auto")] + [(option, option) for option in options]
    ).run()

    return result

def get_hide():
    # Creating a button dialog
    result = yes_no_dialog(
        title="Hide window",
        text="Would you like to hide the command window?"
    ).run()

    return result