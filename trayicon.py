from PIL import Image, ImageDraw, ImageFont
import pystray
import threading
from pystray import MenuItem as item
import win32gui
import win32console
import win32con
import time

from ansi import ansi

class TrayIcon:
    def __init__(self, app, console_hwnd):
        self.icon = None
        self.app = app
        self.console_hwnd = console_hwnd
        print(ansi.OKCYAN + "[TrayIcon] Initialized." + ansi.ENDC)

    def reveal_console(self, icon, item):
        """Reveals the console window."""
        if self.console_hwnd:
            print(ansi.OKCYAN + "[TrayIcon] Revealing console window..." + ansi.ENDC)
            win32gui.ShowWindow(self.console_hwnd, win32con.SW_SHOW)
            time.sleep(2)
            win32gui.SetForegroundWindow(self.console_hwnd)  # Bring it to the front
        else:
            print("Console window handle not found.")

    def create_image(self, answer="", color="black"):
        # Create an image for the icon
        print(ansi.OKCYAN + "[TrayIcon] Creating icon image..." + ansi.ENDC)

        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Set background color
        draw.rectangle((0, 0, width, height), fill=color)

        # Load a custom font with a larger size
        try:
            font = ImageFont.truetype("arial.ttf", 32)  # You can change the font and size here
        except IOError:
            font = ImageFont.load_default()  # Fallback to default font if custom font isn't found

        text = answer

        # Calculate the bounding box of the text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # Position text at the center
        text_x = (width - text_width) / 2
        text_y = (height - text_height) / 2

        # Draw the text on the icon
        draw.text((text_x, text_y), text, fill="white", font=font)

        print(ansi.OKCYAN + "[TrayIcon] Icon image created." + ansi.ENDC)

        return image

    def display_answer(self, answer, color="black"):
        """Displays the answer in the taskbar using a system tray icon."""

        if self.icon is not None:
            self.icon.stop()  # Stop the previous icon if it exists

        max_length = 120
        if len(answer) > max_length:
            answer = answer[:max_length] + "..."  # Truncate and add "..."

        # Create a new icon
        self.icon = pystray.Icon("Gemini Answer")
        self.icon.icon = self.create_image(answer, color=color)
        self.icon.title = answer

        # Create a right-click menu with "Quit" option
        self.icon.menu = pystray.Menu(
            item('Quit', lambda icon, item: self.app.quit()),  # Stops the icon when clicked
            item('Reveal', self.reveal_console)
        )

        # Run the icon in the system tray
        threading.Thread(target=self.icon.run, daemon=True).start()

    def set_loading(self):
        """Displays a loading icon in the taskbar using a system tray icon."""

        if self.icon is not None:
            self.icon.stop()  # Stop the previous icon if it exists

        print(ansi.OKCYAN + "[TrayIcon] Displaying loading icon..." + ansi.ENDC)

        # Create a new icon
        self.icon = pystray.Icon("Gemini Answer")
        self.icon.icon = self.create_image("...", color="orange")
        self.icon.title = "Loading..."

        # Create a right-click menu with "Quit" option
        self.icon.menu = pystray.Menu(
            item('Quit', lambda icon, item: self.app.quit())
        )

        # Run the icon in the system tray
        threading.Thread(target=self.icon.run, daemon=True).start()