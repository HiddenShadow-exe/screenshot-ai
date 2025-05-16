import os
import tempfile
import requests
import pyautogui

from google import genai

from ansi import ansi
from trayicon import TrayIcon

client = None

API_KEY_FILE = "../apikey.txt"
try:
    with open(API_KEY_FILE, "r") as file:
        key = file.read().strip()
    if not key:
        print(ansi.ERROR_MSG + f"API key file '{API_KEY_FILE}' is empty. Exiting.")
        exit()
    
    client = genai.Client(api_key=key)
    print(ansi.SUCCESS_MSG + "API key loaded successfully.")

except FileNotFoundError:
    print(ansi.ERROR_MSG + f"API key file '{API_KEY_FILE}' not found.")
    print("Please create a file named 'apikey.txt' in the same directory and paste your API key inside.")
    exit()
except Exception as e:
    print(ansi.ERROR_MSG + f"An unexpected error occurred while loading the API key: {e}")
    exit()


def take_screenshot():
    """Takes a screenshot and saves it to a temp directory."""
    temp_image_path = os.path.join(tempfile.gettempdir(), "question_screenshot.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(temp_image_path)
    return temp_image_path

def load_image_part(image_path):
    """Loads an image from a file path and prepares it as a Gemini content part."""
    try:
        uploaded_file = client.files.upload(file=image_path)
        return uploaded_file
    except FileNotFoundError:
        print(ansi.ERROR_MSG + f"Image file not found at {image_path}")
        return None
    except Exception as e:
        print(ansi.ERROR_MSG + f"Error loading or processing image {image_path}: {e}")
        return None
    

def upload_pdf_part(pdf_source):
    """
    Handles uploading a PDF file (local path or URL) to Gemini and
    returns the file_data dictionary for the contents list.
    """
    is_url = pdf_source.lower().startswith('http') or pdf_source.lower().startswith('https')
    file_bytes = None
    file_name = None

    try:
        if is_url:
            print(f"Attempting to download PDF from {pdf_source}...")
            response = requests.get(pdf_source, stream=True, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            file_bytes = response.content
            file_name = os.path.basename(requests.utils.urlparse(pdf_source).path) or 'uploaded_pdf.pdf'
            print(f"Download successful ({len(file_bytes)} bytes).")

        else:
            print(f"Attempting to read local PDF file {pdf_source}...")
            if not os.path.exists(pdf_source):
                print(ansi.ERROR_MSG + f"Local PDF file not found at {pdf_source}")
                return None
            with open(pdf_source, 'rb') as f:
                file_bytes = f.read()
            file_name = os.path.basename(pdf_source)
            print(f"File read successfully ({len(file_bytes)} bytes).")

        if not file_bytes:
            print(ansi.ERROR_MSG + f"No content obtained from {pdf_source}.")
            return None

        # Upload the file using the genai client
        print(f"Uploading file '{file_name}' to Gemini...")
        # display_name helps the model distinguish between files, optional but recommended
        uploaded_file = client.upload_file(data=file_bytes, display_name=file_name)
        print(f"File uploaded successfully. File URI: {uploaded_file.uri}")

        # The API expects a dictionary referencing the uploaded file URI
        return {
            'file_data': {
                'mime_type': 'application/pdf', # Specify PDF mime type
                'file_uri': uploaded_file.uri
            }
        }

    except requests.exceptions.RequestException as e:
        print(ansi.ERROR_MSG + f"Error downloading PDF from {pdf_source}: {e}")
        return None
    except FileNotFoundError:
        # This case is handled by the os.path.exists check above, but keeping for completeness
        print(ansi.ERROR_MSG + f"Local PDF file not found at {pdf_source}")
        return None
    except Exception as e:
        # Catch any other unexpected exceptions during reading/uploading
        print(ansi.ERROR_MSG + f"An unexpected error occurred during PDF upload processing for {pdf_source}: {e}")
        return None
    

def create_gemini_contents(image_path, pdf_sources):
    """
    Creates the list of content parts for the Gemini API call.
    Includes the image, uploaded PDF files, and the instruction prompt.
    """
    contents = []

    # 1. Add Image Part
    image_part = load_image_part(image_path)
    if image_part is None:
        print(ansi.ERROR_MSG + "Cannot proceed without a valid image part.")
        return None
    contents.append(image_part)
    print(ansi.SUCCESS_MSG + "Image added.")

    # 2. Add Uploaded PDF Parts (Only if upload is successful)
    uploaded_pdf_parts = []
    for source in pdf_sources:
        pdf_part = upload_pdf_part(source)
        if pdf_part:
            uploaded_pdf_parts.append(pdf_part)

    if uploaded_pdf_parts:
        contents.extend(uploaded_pdf_parts)
        print(ansi.SUCCESS_MSG + f"Successfully added {len(uploaded_pdf_parts)} uploaded PDF file parts.")
    else:
        print(ansi.WARNING_MSG + "No usable PDF files were uploaded from the provided sources.")


    # 3. Add the Final Instruction Text Part (Guides the model on how to respond)
    instruction_prompt ="""
    Based on the question asked in the image and the content of the provided documents, answer the question.
    Answer as concisely as possible.
    If it is a multiple choice question (e.g., asking for A, B, C, D), respond *only* with the single letter (A, B, C, D, etc.) corresponding to the correct answer. Do not include any other text or punctuation.
    If it is not a multiple choice question, answer in as few words as possible.
    Your entire response must be strictly less than 128 characters.
    Do not include any introductory phrases like "The answer is", "Based on the text", etc. Just provide the answer. Do not put newlines in your answer.
    """
    contents.append(instruction_prompt.strip())
    print(ansi.SUCCESS_MSG + "Instruction prompt added.")

    # Basic check: Do we have at least the image and instruction prompt?
    if any(part is None for part in contents) or len(contents) < 2:
        print(ansi.ERROR_MSG + "Content creation failed. Missing image or instruction prompt.")
        return None

    return contents


def call_gemini_multimodal(contents):
    """Calls the Gemini API with the list of multimodal content parts."""

    try:
        print(ansi.INFO_MSG + "Calling Gemini API...")
        # Use the model specified by the user
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=contents,
        )

        # Access the text response
        if not hasattr(response, 'text') or not response.text:
            print(ansi.WARNING_MSG + "API returned an empty response or no text content.")
            # Check for block reasons from the API
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                if response.prompt_feedback.block_reason:
                    print(f"API blocked response: {response.prompt_feedback.block_reason}")
                    if response.prompt_feedback.block_reason_message:
                        print(f"Block message: {response.prompt_feedback.block_reason_message}")
                else:
                    print("API returned no text, but no specific block reason provided in feedback.")

            return None

        answer = response.text.strip()

        print(response.usage_metadata.total_token_count, "tokens used.")

        # Although the prompt asks the model to keep it under 128, we add this check as a safeguard and warning.
        if len(answer) > 128:
            print(ansi.WARNING_MSG + f"API response length ({len(answer)}) exceeded the requested 128 characters.")

        return answer

    except Exception as e:
        if (e.__class__.__name__ == "LocalProtocolError"):
            print(ansi.FAIL + "INVALID API KEY: " + ansi.ENDC + e.__str__())

        else:
            print(ansi.ERROR_MSG + e.__str__())

        return None
    
def process_question(trayicon: TrayIcon, pdf_sources_list):
    # Take a screenshot of the current screen
    image_path = take_screenshot()
    if not os.path.exists(image_path):
        print(ansi.ERROR_MSG + f"Image file not found at '{image_path}'.")
        return
    
    # Prepare content and call API
    print(ansi.INFO_MSG + "Preparing content for Gemini...")

    contents = create_gemini_contents(image_path, pdf_sources_list)

    if contents:
        trayicon.set_loading()
        response_text = call_gemini_multimodal(contents)

        print(ansi.INFO_MSG + ansi.BOLD + ansi.UNDERLINE + "Response from Gemini:" + ansi.ENDC, end=" ")
        if response_text is not None:
            print(ansi.BOLD + response_text + ansi.ENDC)
            trayicon.display_answer(response_text)
        else:
            print(ansi.ERROR_MSG + "Failed to get a valid response from the API.")
            trayicon.display_answer("ERR", color="red")
    else:
        print(ansi.ERROR_MSG + "Failed to prepare content for the API call (image or PDF upload failed).")
        trayicon.display_answer("ERR", color="red")

    # Cleanup: Remove the temporary image file
    try:
        os.remove(image_path)
        print(ansi.INFO_MSG + "Temporary image file removed.")
    except Exception as e:
        print(ansi.ERROR_MSG + f"Failed to remove temporary image file '{image_path}': {e}")

