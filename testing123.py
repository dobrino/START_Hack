from flask import Flask, render_template, request, flash
import app
import calculations as c

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template("index.html", peak_power = c.get_peak_power(50))



if __name__ == '__main__':
    app.run(port=5000)
