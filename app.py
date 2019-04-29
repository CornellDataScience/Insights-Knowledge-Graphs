from flask import Flask, request, render_template
import main
import subprocess

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    main.main(text)
    subprocess.call("git add -A", shell=True)
    subprocess.call("git commit -m \"Run from app\"", shell=True)
    subprocess.call("git push", shell=True)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)