from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = b'mangomango'

# app routing to url
@app.route("/mango")
def index():
    flash("Flashy flashy")
    return render_template("index.html")
