import os
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for
from flask_cors import CORS
import numpy as np
from skimage import color
from PIL import Image
import qrcode
from io import BytesIO

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route('/')
def home_redirect():
    return redirect('/index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/info.html')
def info_page():
    return render_template('info.html')

@app.route('/analyze.html')
def analyze_page():
    return render_template('analyze.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    image_file = request.files['image']
    x = int(request.form['x'])
    y = int(request.form['y'])

    img = Image.open(image_file.stream).convert("RGB")
    np_img = np.array(img)
    lab_img = color.rgb2lab(np_img / 255.0)

    h, w = lab_img.shape[:2]
    Y, X = np.ogrid[:h, :w]
    mask = (X - x)**2 + (Y - y)**2 <= 20**2
    region = lab_img[mask]

    avg_lab = np.mean(region, axis=0)
    return jsonify({
        "L": round(float(avg_lab[0]), 2),
        "a": round(float(avg_lab[1]), 2),
        "b": round(float(avg_lab[2]), 2),
    })

# ✅ QR แบบถาวร: สร้างตามโดเมนจริงของ Render
@app.route('/qr.png')
def qr_png():
    # url_for(..., _external=True) จะให้ URL สมบูรณ์ตามโดเมนที่เรียกจริงบน Render
    target_url = url_for('index', _external=True)  # ชี้ไป index.html
    img = qrcode.make(target_url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render จะส่ง PORT มาให้
    app.run(host='0.0.0.0', port=port)
