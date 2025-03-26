import time
import pynput

from ansi import ansi

positions = []
mouse = pynput.mouse.Controller()

promts = [
    "input field of Gemini.",
    "scroll area (blank space) next to the paragraph.",
    "answer text after scrolling down all the way."
]

position_texts = [
    "Input field",
    "Scroll area",
    "Answer text"
]

def on_click(x, y, button, pressed):
    if pressed:
        positions.append((x, y))
        print(f"Position recorded: X={x}, Y={y}")
        return False  # Stop listening after the first click

print(ansi.OKCYAN + "You will be prompted to click on different parts of the Gemini window." + ansi.ENDC)

for i in range(3):
    input(ansi.OKBLUE + f"Press Enter and then click on the {promts[i]}" + ansi.ENDC)
    
    with pynput.mouse.Listener(on_click=on_click) as listener:
        listener.join()  # Wait for a click

print(ansi.OKGREEN + "\nPositions recorded successfully." + ansi.ENDC)
for i, pos in enumerate(positions):
    print(f"{position_texts[i]} position: X={pos[0]}, Y={pos[1]}")

# Save to file
file_path = "mouse_positions.txt"
with open(file_path, "w") as file:
    file.write(f"Input field: {positions[0]}\n")
    file.write(f"Scroll area: {positions[1]}\n")
    file.write(f"Answer text: {positions[2]}\n")

print(ansi.OKGREEN + f"[SUCCESS] Mouse positions stored in {file_path}." + ansi.ENDC)
time.sleep(2)  # Wait for 2 seconds before closing