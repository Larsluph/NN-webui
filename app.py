from base64 import b64decode

from flask import Flask, render_template, request, jsonify

from ai.mnist import run_model

app = Flask(__name__)
app.secret_key = r'4c44309dd5a080a06e7d67c91cd53fa30012e6296e6258ceb06276a8c06c5e01'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.get_json()
        # image starts with "data:image/png;base64,"
        image_data = data['image'][22:]
        image_bytes = b64decode(image_data)
        prediction = run_model(image_bytes)
        return jsonify({'prediction': prediction})
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
