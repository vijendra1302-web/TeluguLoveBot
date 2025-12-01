# app.py

from fastapi import FastAPI, Form, HTTPException
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
from dotenv import load_dotenv

# Load secret keys from the .env file (to be set on Vercel)
load_dotenv()

# Set variables for WhatsApp API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
BOT_HANDLE = "TeluguLoveBot" # Your Instagram/Bot handle

app = FastAPI()

# --- 1. DP Maker Function ---
def create_crush_dp(crush_name):
    """Generates the DP using the user's provided name."""
    try:
        # Load the template file (You must upload 'template.png')
        img = Image.open("template.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # Load the Telugu Font file (You must upload 'Telugu_Font.ttf')
        try:
            # Adjust font size as needed
            font = ImageFont.truetype("Telugu_Font.ttf", 80) 
        except IOError:
            # Fallback to default font if Telugu font is not found
            font = ImageFont.load_default()

        # Draw the crush name in the center
        text_width, text_height = draw.textbbox((0, 0), crush_name, font=font)[2:]
        x = (img.width - text_width) / 2
        y = (img.height / 2) - (text_height / 2)
        draw.text((x, y), crush_name, fill=(255, 255, 255), font=font)
        
        # Watermark (Bot Handle)
        wm_font = ImageFont.truetype("arial.ttf", 25)
        draw.text((20, img.height - 40), f"Made by @{BOT_HANDLE}", fill=(255, 255, 0, 180), font=wm_font)

        # Save the image in memory
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    except Exception as e:
        # This error often occurs if template.png or the font file is missing.
        print(f"DP Creation Error: {e}")
        return None

# --- 2. WhatsApp Message Handler (Webhook Endpoint) ---
@app.post("/webhook")
async def handle_whatsapp_message(
    Body: str = Form(None), 
    From: str = Form(None), 
    ProfileName: str = Form(None)
):
    """Receives and processes incoming WhatsApp messages."""
    if not Body:
        raise HTTPException(status_code=400, detail="No message body received")

    # Keyword check: look for 'dp' or 'డిపి'
    if "dp" in Body.lower() or "డిపి" in Body.lower():
        parts = Body.split()
        if len(parts) >= 2:
            crush_name = " ".join(parts[1:]) 
        else:
            send_whatsapp_message(From, "Please send in the format 'DP <Name>'. Example: 'DP Kavitha'")
            return {"status": "ok"}
        
        # Generate DP
        dp_data = create_crush_dp(crush_name)
        
        if dp_data:
            # IMPORTANT: In a real scenario, you'd upload the image data and send the URL.
            # For now, we confirm the creation.
            send_whatsapp_message(From, f"Your DP for '{crush_name}' is ready! Check your status for sharing instructions. 💖")
        
        else:
            send_whatsapp_message(From, "Sorry! An error occurred while creating the DP. Please ensure the template and font files are uploaded correctly.")
    else:
        # Default response for other messages
        send_whatsapp_message(From, f"Hi {ProfileName}! For your 'Crush Name DP', send 'DP <Name>'. Example: DP Lakshmi.")
    
    return {"status": "ok"}

# --- 3. WhatsApp Response Function Placeholder ---
def send_whatsapp_message(to_number, message_body):
    """Sends a message via the WhatsApp API."""
    # This is a placeholder. Real code requires Meta Cloud API integration.
    # We skip the heavy lifting for the zero-investment setup.
    pass 

# --- Vercel/Meta Webhook Verification ---
@app.get("/webhook")
async def verify_webhook(
    "hub.mode": str = None, 
    "hub.challenge": str = None, 
    "hub.verify_token": str = None
):
    """Verifies the webhook for Meta."""
    # VERIFY_TOKEN is set as an environment variable in Vercel.
    VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "YOUR_SECRET_TOKEN") 
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    
    raise HTTPException(status_code=403, detail="Verification token mismatch")
