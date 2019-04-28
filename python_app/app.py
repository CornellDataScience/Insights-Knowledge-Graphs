from flask import Flask, request, render_template
from scrape import read_page
from tuples_generator import main

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    raw_data = read_page(text)
    return main(raw_data)

@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)