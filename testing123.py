from flask import Flask, render_template, request, flash, redirect, url_for
import app as a
import calculations as c

app = Flask(__name__)
app.secret_key = "mangomango"
global area


@app.route('/', methods=["POST", "GET"])
def hello():
    if request.method == "POST":
        area, img = a.calculate_stats(request.form["nm"])
        print(area)

        pcost = c.get_panel_costs_by_area(area)
        icost = c.get_inverter_costs(area)
        inscost = c.get_initial_investment_costs(area)

        return render_template("index.html",
                               self_consumption_50 = c.get_yearly_revenue(area, .5),
                               self_consumption_30 = c.get_yearly_revenue(area, .3),
                               self_consumption_15 = c.get_yearly_revenue(area, .15),
                               panel_cost=c.get_panel_costs_by_area(area),
                               inverter_cost=c.get_inverter_costs(area),
                               installation_cost=c.get_initial_investment_costs(area),
                               total_cost = round(pcost + icost + inscost,2),
                               roof_area=area,
                               peak_power=c.get_peak_power(area),
                               break_even=c.get_break_even_time(area, .3))
    return render_template("index.html", self_consumption_50=0, peak_power=0)


@app.route('/#result')
def result():
    return render_template("index.html", peak_power=c.get_peak_power(1000))


if __name__ == '__main__':
    app.run(port=5000)
