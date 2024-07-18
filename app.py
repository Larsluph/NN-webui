from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        num1 = request.form.get('input_layer')
        num2 = request.form.get('hidden_layer')
        num3 = request.form.get('output_layer')
        # You can process the numbers here
        return f"Received numbers: {num1}, {num2}, {num3}"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
