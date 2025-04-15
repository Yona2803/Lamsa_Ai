import os
import sys
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
### from .env file (default)
load_dotenv('.env')

### from .env.local file (overrides and allow overriding)
load_dotenv('.env.local', override=True)

# Access specific variables
geminiApiKey = os.getenv("GEMINI_API_KEY")

if not geminiApiKey:
    print("Error: No API key found. Please set GEMINI_API_KEY in your environment variables.")
    sys.exit(1)

def getImageData(imagePath):
    """Read an image and return it as a base64 string"""
    try:
        # Open the image
        with Image.open(imagePath) as img:
            # Convert to RGB if necessary (e.g., for PNG with transparency)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            imageBytes = buffer.getvalue()
            
        # Encode as base64
        return base64.b64encode(imageBytes).decode('utf-8')
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def generateGeminiResponse(imagePath, textPrompt):
    """Generate a response using Gemini API with text prompt and optional image"""
    try:
        print(f"Configuring Gemini API with key: {geminiApiKey[:5]}...{geminiApiKey[-5:] if geminiApiKey else 'None'}")
        
        # Configure Gemini
        genai.configure(api_key=geminiApiKey)
        
        # Create the model
        print("Creating Gemini model...")
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Prepare content parts
        contentParts = [textPrompt]
        
        # Add image if provided
        if imagePath:
            imageData = getImageData(imagePath)
            if imageData:
                imagePart = {
                    "mime_type": "image/jpeg",
                    "data": imageData
                }
                contentParts.append(imagePart)
                print("Image processed and added to request")
            else:
                print("Failed to process image, continuing with text only")
        
        print("Sending request to Gemini API...")
        response = model.generate_content(contentParts)
        
        if response:
            result = response.text
            print("Received response from Gemini API")
            return result
        else:
            print("No valid response received from Gemini")
            return None
            
    except Exception as e:
        print(f"Error in generateGeminiResponse: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test the functionality directly
if __name__ == "__main__":
    print("Testing Gemini Backend directly")
    textPrompt = input("Enter your text prompt: ")
    
    useImage = input("Do you want to include an image? (y/n): ").lower() == 'y'
    imagePath = None
    
    if useImage:
        imagePath = input("Enter the path to your image: ")
        if not os.path.exists(imagePath):
            print(f"Image not found at {imagePath}")
            useImage = False
            imagePath = None
    
    result = generateGeminiResponse(imagePath, textPrompt)
    if result:
        print(f"Success! Result: \n{result}")
    else:
        print("Failed to generate response")