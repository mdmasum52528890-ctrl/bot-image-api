from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import os

app = Flask(__name__)

def get_font(size):
    if not os.path.exists("font.ttf"):
        r = requests.get("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf")
        with open("font.ttf", "wb") as f:
            f.write(r.content)
    return ImageFont.truetype("font.ttf", size)

def draw_text_auto_size(draw, text, position, max_width, initial_size):
    size = initial_size
    font = get_font(size)
    while font.getlength(text) > max_width and size > 10:
        size -= 1
        font = get_font(size)
    draw.text(position, text, font=font, fill="white", anchor="mm")

@app.route('/generate')
def generate():
    name = request.args.get('name', '')
    username = request.args.get('username', '')
    user_id = request.args.get('id', '')
    balance = request.args.get('balance', '0.00')
    invited = request.args.get('invited', '0')
    avatar_url = request.args.get('avatar', '')

    bg_url = "https://i.postimg.cc/52mT8XnZ/20260423-145947.jpg"
    response = requests.get(bg_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    if avatar_url:
        try:
            av_res = requests.get(avatar_url)
            avatar = Image.open(BytesIO(av_res.content)).convert("RGBA")
            avatar = avatar.resize((300, 300))
            
            mask = Image.new('L', (300, 300), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 300, 300), fill=255)
            
            avatar_circular = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            img.paste(avatar_circular, (490, 210), avatar_circular)
        except:
            pass

    draw = ImageDraw.Draw(img)
    
    draw_text_auto_size(draw, name, (160, 240), 280, 35)
    draw_text_auto_size(draw, invited, (160, 450), 280, 35)
    draw_text_auto_size(draw, user_id, (160, 660), 280, 35)
    
    draw_text_auto_size(draw, "0", (1120, 240), 280, 35)
    draw_text_auto_size(draw, balance, (1120, 450), 280, 35)
    draw_text_auto_size(draw, username, (1120, 660), 280, 35)

    img_io = BytesIO()
    img.convert("RGB").save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
