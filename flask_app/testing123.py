from flask import Flask, render_template, request
from app import calculate_rooftop_area
import calculations as c

app = Flask(__name__)
app.secret_key = "mangomango"
global area
default_page = "index.html"


@app.route('/', methods=["POST", "GET"])
def hello():
    # fallback logic for handling non-POST request
    if request.method != "POST":
        # TODO: put a more meaningful error page that doesn't cause a HTTP 500
        render_template(default_page, self_consumption_50=0, peak_power=0)

    address = request.form["nm"]
    area, img = calculate_rooftop_area(address)
    print(area)
    # TODO: do something with the image (e.g. show it to the user to ensure it's the correct house)

    pcost = c.get_panel_costs_by_area(area)
    icost = c.get_inverter_costs(area)
    inscost = c.get_initial_investment_costs(area)

    return render_template(default_page,
                           self_consumption_50=c.get_yearly_revenue(area, .5),
                           self_consumption_30=c.get_yearly_revenue(area, .3),
                           self_consumption_15=c.get_yearly_revenue(area, .15),
                           panel_cost=c.get_panel_costs_by_area(area),
                           inverter_cost=c.get_inverter_costs(area),
                           installation_cost=c.get_initial_investment_costs(area),
                           total_cost=round(pcost + icost + inscost, 2),
                           roof_area=area,
                           peak_power=c.get_peak_power(area),
                           break_even=c.get_break_even_time(area, .3))


@app.route('/#result')
def result():
    return render_template(default_page, peak_power=c.get_peak_power(1000))


if __name__ == '__main__':
    app.run(port=5000)
