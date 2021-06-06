from flask import (
    Flask,
    send_file,
    render_template,
    jsonify,
    redirect
)
from flask_cors import CORS


from PIL import ImageDraw, Image, ImageFont
import secrets
import numpy as np
from io import BytesIO
import datetime


app = Flask(__name__)
CORS(app)
CAPTCHAS = {}
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


"""
function for deleting keys in a dictionary because del KEY[key] is not enough
"""
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


"""
generate random characters
"""
def random_char(y):
    str1 = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ'
    return ''.join(secrets.choice(str1) for _ in range(y))


"""
add the noise lines, takes 1 parameter draw which is d when using it
1st & second for loops >> add lines, 2 of them so theyre positioned differently
"""
def add_noise_lines(draw):
    size = (305, 95)

    for _ in range(1):
        width = secrets.choice((1, 2))
        start = (0, secrets.choice(range(0, size[1] - 1)))
        end = (size[0], secrets.choice(range(0, size[1] - 1)))
        draw.line([start, end], fill="white", width=width)

    for _ in range(1):
        start = (-50, -50)
        end = (size[0] + 10, secrets.choice(range(0, size[1] + 10)))
        draw.arc(start + end, 0, 360, fill="white")
    return draw


"""
add the salt and pepper effect to our images using numpy
"""
def salt_and_pepper(image, prob):
    arr = np.asarray(image)
    original_dtype = arr.dtype
    intensity_levels = 2 ** (arr[0, 0].nbytes * 8)
    min_intensity = 0
    max_intensity = intensity_levels - 1
    random_image_arr = np.random.choice(
        [min_intensity, 1, np.nan], p=[prob / 2, 1 - prob, prob / 2], size=arr.shape
    )
    salt_and_peppered_arr = arr.astype(np.float_) * random_image_arr
    salt_and_peppered_arr = np.nan_to_num(
        salt_and_peppered_arr, nan=max_intensity
    ).astype(original_dtype)

    return Image.fromarray(salt_and_peppered_arr)

"""
fonts for the letters
fonts_lower >> lowercase
fonts_upper >> uppercase
"""
fonts_lower = [
    ImageFont.truetype("./fonts/lower/gadugib.ttf", 30),
    ImageFont.truetype("./fonts/lower/Chalkduster_400.ttf", 30),
    ImageFont.truetype('./fonts/lower/ShadowsIntoLight-Regular.ttf', 30),
    ImageFont.truetype('./fonts/lower/Rajdhani-SemiBold.ttf', 30)
]
fonts_upper = [
    ImageFont.truetype('./fonts/upper/arial.ttf', 55),
    ImageFont.truetype('./fonts/upper/FallingSky-JKwK.ttf', 55),
    ImageFont.truetype('./fonts/upper/TrainOne-Regular.ttf', 55),
    ImageFont.truetype('./fonts/upper/BebasNeue-Regular.ttf', 55)
]


"""
place where the captchas are generated
everything not mentioned >> self explanatory
1st for loop >> assign proper fonts
2nd for loop >> position text, all 1 by 1 that way theyre randomly positioned
3rd for loop >> draw a striking line
"""
def capGen(text):
    text_color = 255, 255, 255
    image_color = 128, 128, 128
    right, height = 0, 0
    corresponding_font = {}
    textPositions = []

    img = Image.new('RGB', (300, 100), color=image_color)
    img.load()
    d = ImageDraw.Draw(img)
    d = add_noise_lines(d)

    for let in text:
        if let.isupper():
            corresponding_font[let] = secrets.choice(fonts_upper)
        elif let.islower():
            corresponding_font[let] = secrets.choice(fonts_lower)

    for count, letter in enumerate(text):
        cords = secrets.choice(range(20, 29)) + right, secrets.choice(range(2, 9)) + height
        d.text(cords, f"{letter}", fill=text_color, font=corresponding_font[letter])
        right += secrets.choice(range(36, 51)) + count
        height += secrets.choice(range(-5, 11))
        textPositions.append(tuple(map(secrets.choice(range(15, 25)).__add__, cords)))

    for i in range(len(textPositions) - 1):
        d.line((textPositions[i], textPositions[i + 1]), fill=(255, 255, 255))

    return img


"""
CDN (content delivery network) for the API, images ARE generated here incase they have not been already
first if >> check if captcha expired, if yes remove it and raise error
second if >> if a PIL image object is not already generate it, generate and cache
third if >> captcha is there, not expired, show it as normal
"""
@app.route('/api/cdn/<key>')
def get_img(key):
    try:
        if datetime.datetime.utcnow() > CAPTCHAS[key][2]:
            removekey(CAPTCHAS, key)
            raise KeyError

        if not CAPTCHAS[key][1]:
            PILimage = capGen(text=CAPTCHAS[key][0])
            PILimage = salt_and_pepper(PILimage, prob=0.13)
            output = BytesIO()
            PILimage.convert('RGBA').save(output, format='PNG')
            output.seek(0, 0)

            CAPTCHAS[key][1] = PILimage
            return send_file(output, mimetype='image/png', as_attachment=False)
        else:
            output = BytesIO()
            CAPTCHAS[key][1].convert('RGBA').save(output, format='PNG')
            output.seek(0, 0)

            return send_file(output, mimetype='image/png', as_attachment=False)
    except KeyError:
        return render_template('404pg.html')


"""
the main API endpoint, images are NOT generated here
----------------------------------------------------
txt >> captcha solution
_ID >> captcha ID in the backend
delta, now >> datetime objects for ratelimiting
"""
@app.route('/api/img')
def api_captcha():
    txt = random_char(secrets.choice((5, 6)))
    _ID = random_char(50)

    delta = datetime.timedelta(minutes=5)
    now = datetime.datetime.utcnow()

    future = now + delta
    if _ID not in CAPTCHAS:
        CAPTCHAS[_ID] = [txt, None, future]

    return jsonify({'solution': txt,
                    'url': f'http://127.0.0.1:5000/api/cdn/{_ID}'
                    })


"""
basic API endpoints
"""
@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/examples')
def ex():
    return render_template("examples.html")

@app.route('/')
def home():
    return render_template("index.html")

"""
error handling
"""
@app.errorhandler(404)
def not_found(e):
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
