from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import numpy as np
from skimage import color
from PIL import Image
import qrcode
from pyngrok import ngrok, conf

# ตั้งค่า ngrok
ngrok.set_auth_token("30jV5mUc7UGqQdUvbJWDLUvCv11_7oYbPaDFmEGm9RmmmmHHc")
conf.get_default().region = "ap"

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
        "L": round(avg_lab[0], 2),
        "a": round(avg_lab[1], 2),
        "b": round(avg_lab[2], 2),
    })

if __name__ == '__main__':
    tunnel = ngrok.connect(5000, bind_tls=True)
    public_url = tunnel.public_url  # ✅ สำคัญ

    print(f"\n🔗 เปิดใช้งานที่: {public_url}/index.html")

    try:
        qr_url = f"{public_url}/index.html"
        img = qrcode.make(qr_url)
        img.save("static/qr_code.png")
        print(f"📱 QR สำหรับสแกน: {qr_url}")
    except Exception as e:
        print("⚠️ สร้าง QR ไม่สำเร็จ:", e)

    app.run(host='0.0.0.0', port=5000)