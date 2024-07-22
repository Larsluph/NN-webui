from flask import Flask, render_template, request, flash, redirect, jsonify
from ai import mnist

app = Flask(__name__)
app.secret_key = r'4c44309dd5a080a06e7d67c91cd53fa30012e6296e6258ceb06276a8c06c5e01'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        image = request.files['image']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if image.filename == '':
            flash('No selected file')
            return redirect(request.url)

        prediction = mnist.run_model(image.read())
        return render_template('index.html', prediction=prediction)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
