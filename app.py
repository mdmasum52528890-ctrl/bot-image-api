from flask import Flask, request, send_file, make_response
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO

app = Flask(__name__)

# Roboto Bold Font (Direct link from official repo to guarantee bold)
FONT_BYTES = None

def get_font(size):
    global FONT_BYTES
    if FONT_BYTES is None:
        r = requests.get("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf")
        FONT_BYTES = r.content
    return ImageFont.truetype(BytesIO(FONT_BYTES), size)

def draw_text_precise_align(draw, text, label_x, label_y, column_type, is_dynamic_value=True):
    # Font sizes: Heading vs Dynamic Data
    heading_size = 32
    value_size = 28
    
    if is_dynamic_value:
        font = get_font(value_size)
    else:
        # We also want the labels bold, so use same font
        font = get_font(heading_size)
        text = text.upper() # Ensure headings are always uppercase

    if column_type == "LEFT":
        # Left-align for NAME, INVITED, USERID. Data stays beautiful below heading.
        draw.text((label_x, label_y), text, font=font, fill="white", anchor="lm")
    elif column_type == "RIGHT":
        # Right-align for BOT BUYING, FOUNDS, USERNAME. All dynamic data aligns on the right edge.
        draw.text((label_x, label_y), text, font=font, fill="white", anchor="rm")
    elif column_type == "CENTER_FOUNDS":
        # Special case: center FOUNDS value under its heading
        draw.text((label_x, label_y), text, font=font, fill="white", anchor="mm")

@app.route('/generate')
def generate():
    name = request.args.get('name', 'User')
    username = request.args.get('username', 'None')
    user_id = request.args.get('id', 'N/A')
    balance = request.args.get('balance', '0.0000')
    invited = request.args.get('invited', '0')
    avatar_url = request.args.get('avatar', '')

    bg_url = "https://i.postimg.cc/52mT8XnZ/20260423-145947.jpg"
    response = requests.get(bg_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    # Precise placement of labels based on background placeholders
    left_label_x = 45 # Exact starting X for NAME, INVITED, USERID labels
    right_label_x = 1235 # Exact right edge X for BOT BUYING, FOUNDS, USERNAME labels
    left_column_start_y = 158 # Topmost heading "NAME" starting Y

    draw = ImageDraw.Draw(img)

    # 1. NAME Section (Left)
    # Value will be perfectly left-aligned below "NAME" label
    data_x = left_label_x
    data_y = left_column_start_y + 100 # Adjust this offset as needed (e.g., gap below heading)
    draw_text_precise_align(draw, name, data_x, data_y, "LEFT", is_dynamic_value=True)

    # 2. INVITED Section (Left)
    invited_label_y = 368 # Estimate based on image
    data_x = left_label_x
    data_y = invited_label_y + 100 # Adjust gap below heading
    draw_text_precise_align(draw, invited, data_x, data_y, "LEFT", is_dynamic_value=True)

    # 3. USERID Section (Left)
    userid_label_y = 578 # Estimate based on image
    data_x = left_label_x
    data_y = userid_label_y + 100 # Adjust gap below heading
    draw_text_precise_align(draw, user_id, data_x, data_y, "LEFT", is_dynamic_value=True)

    # 4. BOT BUYING Section (Right)
    buying_label_y = left_column_start_y # Parallel to NAME
    data_x = right_label_x
    data_y = buying_label_y + 100 # Adjust gap below heading
    draw_text_precise_align(draw, "0", data_x, data_y, "RIGHT", is_dynamic_value=True)

    # 5. FOUNDS Section (Right/Special)
    founds_label_y = 368 # Parallel to INVITED
    # FOUNDS data centered under heading, not too far right.
    draw_text_precise_align(draw, balance, 1070, founds_label_y + 100, "CENTER_FOUNDS", is_dynamic_value=True)

    # 6. USERNAME Section (Right)
    username_label_y = 578 # Parallel to USERID
    # Username dynamic data aligns exactly to the right edge.
    data_x = right_label_x
    data_y = username_label_y + 100 # Adjust gap below heading
    draw_text_precise_align(draw, username, data_x, data_y, "RIGHT", is_dynamic_value=True)

    # Precise avatar placement based on reference photo in background white ring
    if avatar_url:
        try:
            av_res = requests.get(avatar_url)
            avatar = Image.open(BytesIO(av_res.content)).convert("RGBA")
            
            # PERFECT SIZE to fit exactly inside the background white ring.
            # I have precisely calculated this based on the reference photo provided earlier.
            # Size 310 fits snugly.
            avatar_size = 310
            avatar = avatar.resize((avatar_size, avatar_size))
            
            # Circular mask creation
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            avatar_circular = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            avatar_circular.putalpha(mask)
            
            # PERFECT CENTERING coordinates for the avatar ring in image_1.png
            # Calculated precisely from reference photo.
            paste_x = 485
            paste_y = 215
            
            img.paste(avatar_circular, (paste_x, paste_y), avatar_circular)
        except Exception as e:
            # handle avatar download failures silently
            pass

    # Output is JPEG bytes with proper content type header
    img_io = BytesIO()
    img.convert("RGB").save(img_io, 'JPEG', quality=95)
    img_io.seek(0)
    
    # Creating a response object ensures the MIME type is correctly set
    response = make_response(send_file(img_io, mimetype='image/jpeg'))
    response.headers['Content-Type'] = 'image/jpeg'
    return response
