from flask import (
    Flask,
    send_file,
    render_template,
    jsonify,
    redirect,
    request
)
from flask_cors import CORS

from supportfiles import noise

from PIL import ImageDraw, Image, ImageFont
import secrets as sc
from io import BytesIO
import datetime
import random
import expiringdict

app = Flask(__name__)
CORS(app)
CAPTCHAS = expiringdict.ExpiringDict(max_age_seconds=300, max_len=99999999)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


class CaptchaCnt:
    captcha_counter = 0

"""
fonts for the letters
fonts_lower >> lowercase
fonts_upper >> uppercase
"""
fonts_lower = [
    ImageFont.truetype("./fonts/lower/gadugib.ttf", 28),
    ImageFont.truetype("./fonts/lower/Chalkduster_400.ttf", 28),
    ImageFont.truetype('./fonts/lower/ShadowsIntoLight-Regular.ttf', 28),
    ImageFont.truetype('./fonts/lower/Rajdhani-SemiBold.ttf', 28)
]
fonts_upper = [
    ImageFont.truetype('./fonts/upper/arial.ttf', 53),
    ImageFont.truetype('./fonts/upper/FallingSky-JKwK.ttf', 53),
    ImageFont.truetype('./fonts/upper/TrainOne-Regular.ttf', 53),
    ImageFont.truetype('./fonts/upper/BebasNeue-Regular.ttf', 53)
]

"""
generate random characters
"""
def random_char(y, module):
    string = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKMNOPQRSTUVWXYZ'
    return ''.join(module.choice(string) for _ in range(y))


"""
place where the captchas are generated
everything not mentioned >> self explanatory
1st for loop >> assign proper fonts
2nd for loop >> position text, all 1 by 1 that way theyre randomly positioned also put them at a angle
3rd for loop >> draw a striking line
"""
def capGen(text):
    white = 255, 255, 255
    right, height = 0, 0
    corresponding_font = {
        let: random.choice(
            fonts_upper if let.isupper() else fonts_lower
        )
        for let in text
    }
    textPositions = []

    img = Image.new('RGB', (325, 95), color=(128, 128, 128))
    img.load()
    d = noise.add_noise_lines(ImageDraw.Draw(img))

    for count, letter in enumerate(text):
        cords = sc.randbelow(20) + 19 + right, sc.randbelow(2) + 7 + height
        d.text(cords, f"{letter}", fill=white, font=corresponding_font[letter])
        val = sc.randbelow(36) + 30 + count
        if val < 40:
            right += 20
        right += sc.randbelow(36) + 30 + count

        height += sc.choice(range(-5, 11))
        textPositions.append(
            tuple(sc.randbelow(10) + 15 + i for i in cords)
        )

    for i in range(len(textPositions) - 1):
        d.line((textPositions[i], textPositions[i + 1]), fill=white)

    return img


"""
CDN for the API, images are generated here incase they have not been already
second if >> if a PIL image object is not already generate it, generate and cache
third if >> captcha is there, not expired, show it as normal
"""
@app.route('/api/cdn/<key>')
def get_img(key):
    try:
        if CAPTCHAS[key][3] >= CAPTCHAS[key][4]:
            del CAPTCHAS[key]

        CAPTCHAS[key][3] += 1

        if not CAPTCHAS[key][1]:
            PILimage = noise.salt_and_pepper(capGen(text=CAPTCHAS[key][0]), prob=0.13)
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
        return redirect('/')


"""
the main API endpoint, images are not generated here
----------------------------------------------------
txt >> captcha solution
_ID >> captcha ID in the backend
delta, now >> datetime objects for ratelimiting
"""
@app.route('/api/img')
def api_captcha():
    access = request.args.get('requests', default=10, type=int)

    delta = datetime.timedelta(minutes=5)
    now = datetime.datetime.utcnow()
    future = now + delta

    if access > 20:
        return redirect('/')

    txt = random_char(y=sc.choice((4, 6)),
                      module=sc)

    _ID = random_char(y=10,
                      module=random)

    _ID = str(CaptchaCnt.captcha_counter) + '.' + _ID + '.' + now.strftime('%S')[-5:]

    CAPTCHAS[_ID] = [txt, None, future, 0, access]

    CaptchaCnt.captcha_counter += 1
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
