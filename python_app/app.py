from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('./form.html')

@app.route('/', methods=['POST'])
def handle_data():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text + 'ddd'

@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)