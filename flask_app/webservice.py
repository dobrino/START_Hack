"""This module run a HTTP webserver, yielding a HTML website."""

import sys
from flask import Flask, render_template, request
from solanet.rooftop_area_scan import RooftopAreaScanner
from solanet.solar_plant_profitability import SolarPlantEvaluation


app = Flask(__name__)
app.secret_key = "mangomango"
DEFAULT_PAGE = "index.html"

rooftop_scanner = RooftopAreaScanner()

EMPTY_RESULT = render_template(
    DEFAULT_PAGE,
    self_consumption_50=0,
    self_consumption_30=0,
    self_consumption_15=0,
    panel_cost=0,
    inverter_cost=0,
    installation_cost=0,
    total_cost=0,
    roof_area=0,
    peak_power=0,
    break_even=0
)


@app.route('/', methods=["POST", "GET"])
def hello():
    """Representing a HTTP endpoint for serving potential solar plant
    profitability evaluations, given the house's postal address."""

    # fallback logic for handling non-POST request
    if request.method != "POST":
        return render_template(
            DEFAULT_PAGE,
            self_consumption_50=0,
            self_consumption_30=0,
            self_consumption_15=0,
            panel_cost=0,
            inverter_cost=0,
            installation_cost=0,
            total_cost=0,
            roof_area=0,
            peak_power=0,
            break_even=0
        )

    address = str(request.form["nm"])
    print(f'requesting hello endpoint: {address}', file=sys.stderr)
    area, _ = rooftop_scanner.calculate_rooftop_area(address)
    print(area)
    # TODO: do something with the image (e.g. show it to the user to ensure it's the correct house)

    # TODO: handle the case when the detected area is 0 -> return error message
    if area == 0:
        return render_template(
            DEFAULT_PAGE,
            self_consumption_50=0,
            self_consumption_30=0,
            self_consumption_15=0,
            panel_cost=0,
            inverter_cost=0,
            installation_cost=0,
            total_cost=0,
            roof_area=0,
            peak_power=0,
            break_even=0
        )

    plant_eval = SolarPlantEvaluation(area)
    pcost = plant_eval.common.panel_costs_by_area
    icost = plant_eval.common.inverter_costs
    inscost = plant_eval.common.initial_investment_costs
    total_cost = round(pcost + icost + inscost, 2)

    return render_template(
        DEFAULT_PAGE,
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


if __name__ == '__main__':
    app.run(port=5000)
