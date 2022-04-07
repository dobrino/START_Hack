from flask import Flask, render_template, request
from solanet.rooftop_area_scan import RooftopAreaScanner
from solanet.solar_plant_profitability import SolarPlantEvaluation


app = Flask(__name__)
app.secret_key = "mangomango"
default_page = "index.html"

rooftop_scanner = RooftopAreaScanner()


@app.route('/', methods=["POST", "GET"])
def hello():
    # fallback logic for handling non-POST request
    if request.method != "POST":
        # TODO: put a more meaningful error page that doesn't cause a HTTP 500
        render_template(default_page, self_consumption_50=0, peak_power=0)

    address = request.form["nm"]
    area, img = rooftop_scanner.calculate_rooftop_area(address)
    print(area)
    # TODO: do something with the image (e.g. show it to the user to ensure it's the correct house)

    plant_eval = SolarPlantEvaluation(area)
    pcost = plant_eval.common.panel_costs_by_area
    icost = plant_eval.common.inverter_costs
    inscost = plant_eval.common.initial_investment_costs
    total_cost = round(pcost + icost + inscost, 2)

    return render_template(
        default_page,
        self_consumption_50=plant_eval.plants_by_sc[50].yearly_revenue,
        self_consumption_30=plant_eval.plants_by_sc[30].yearly_revenue,
        self_consumption_15=plant_eval.plants_by_sc[15].yearly_revenue,
        panel_cost=pcost,
        inverter_cost=icost,
        installation_cost=inscost,
        total_cost=total_cost,
        roof_area=area,
        peak_power=plant_eval.common.peak_power,
        break_even=plant_eval.plants_by_sc[30].break_even_years
    )


@app.route('/#result')
def result():
    plant_eval = SolarPlantEvaluation(area=1000)
    return render_template(default_page, peak_power=plant_eval.common.peak_power)


if __name__ == '__main__':
    app.run(port=5000)
