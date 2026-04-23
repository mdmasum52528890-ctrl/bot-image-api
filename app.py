from flask import Flask, request, send_file, make_response
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO

app = Flask(__name__)

FONT_BYTES = None
BG_BYTES = None

def get_font(size):
    global FONT_BYTES
    if FONT_BYTES is None:
        r = requests.get("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf")
        FONT_BYTES = r.content
    return ImageFont.truetype(BytesIO(FONT_BYTES), size)

def draw_text_center(draw, text, x, y, size=35):
    font = get_font(size)
    draw.text((x, y), text, font=font, fill="white", anchor="mm")

def truncate_text(text, max_len=10):
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

@app.route('/generate')
def generate():
    global BG_BYTES
    
    name = request.args.get('name', 'User')
    username = request.args.get('username', 'None')
    user_id = request.args.get('id', 'N/A')
    balance = request.args.get('balance', '0.0000')
    invited = request.args.get('invited', '0')
    avatar_url = request.args.get('avatar', '')

    name = truncate_text(name, 10)
    username = truncate_text(username, 10)

    bg_url = "https://i.postimg.cc/MZQJqdqr/20260423-211051.jpg"
    
    if BG_BYTES is None:
        try:
            response = requests.get(bg_url, timeout=5)
            BG_BYTES = response.content
        except:
            pass
            
    if BG_BYTES:
        img = Image.open(BytesIO(BG_BYTES)).convert("RGBA")
    else:
        img = Image.new("RGBA", (1280, 800), (0,0,0,255))
        
    draw = ImageDraw.Draw(img)

    draw_text_center(draw, name, 245, 235)
    draw_text_center(draw, balance, 640, 160)
    draw_text_center(draw, "00", 1030, 320)
    draw_text_center(draw, invited, 225, 560)
    draw_text_center(draw, user_id, 410, 740)
    draw_text_center(draw, username, 1030, 730)

    if avatar_url:
        try:
            av_res = requests.get(avatar_url, timeout=3)
            avatar = Image.open(BytesIO(av_res.content)).convert("RGBA")
            
            avatar_size = 310
            avatar = avatar.resize((avatar_size, avatar_size))
            
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            avatar_circular = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            paste_x = 485
            paste_y = 215
            img.paste(avatar_circular, (paste_x, paste_y), avatar_circular)
        except:
            pass

    img_io = BytesIO()
    img.convert("RGB").save(img_io, 'JPEG', quality=85)
    img_io.seek(0)
    
    response = make_response(send_file(img_io, mimetype='image/jpeg'))
    response.headers['Content-Type'] = 'image/jpeg'
    return response
