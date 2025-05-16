import os
import time
import keyboard

from trayicon import TrayIcon
from ansi import ansi
from gemini import process_question

quitting = False

def close_program():
    """Closes the program and cleans up resources."""
    print(ansi.INFO_MSG + "Exiting...")
    keyboard.unhook_all_hotkeys()
    global quitting
    quitting = True


if __name__ == "__main__":
    # Init the tray icon with this script's instance
    trayicon = TrayIcon(quit_callback=close_program)
    trayicon.display_answer("RDY", color="green")

    # Get PDF paths/URLs from user input (allow multiple)
    pdf_sources_list = []
    print("\nEnter paths or URLs to PDF documents that provide context (leave blank and press Enter when done):")
    while True:
        pdf_source_input = input(f"PDF source {len(pdf_sources_list) + 1} (local path or URL): ").strip()
        if not pdf_source_input:
            break # Exit loop if input is empty

        # Basic check if it looks like a local file or URL
        is_url_input = pdf_source_input.lower().startswith(('http://', 'https://'))
        if is_url_input or os.path.exists(pdf_source_input):
            pdf_sources_list.append(pdf_source_input)
        else:
            print(ansi.WARNING + f"'{pdf_source_input}' does not look like a valid URL and was not found as a local file. Skipping." + ansi.ENDC)

    print(ansi.SUCCESS_MSG + f"Collected {len(pdf_sources_list)} PDF sources.")
    print("-" * 50)

    print(ansi.OKGREEN + "READY: " + ansi.ENDC + "Press Ctrl+Shift+Q to process the question.")
    print(ansi.INFO_MSG + "Press Ctrl+Alt+Shift+C to quit.")

    keyboard.add_hotkey("ctrl+shift+q", lambda: process_question(trayicon, pdf_sources_list))
    keyboard.add_hotkey("ctrl+alt+shift+c", lambda: close_program())

    # Keep the script running to listen for hotkeys
    try:
        while not quitting:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(ansi.INFO_MSG + "Keyboard interrupt detected.")
        close_program()
    except Exception as e:
        print(ansi.ERROR_MSG + f"An unexpected error occurred: {e}")
        close_program()
