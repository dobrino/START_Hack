"""This module provides profitability calculations for deciding
whether to install a solar power plant on top of a given house."""

solarRadiation = 1
efficiency = .25
specific_efficiency = [26, 59, 72, 128, 124, 155, 131, 123, 89, 63, 27, 21]
price_per_kwh_ownConsumption = 0.3
price_per_kwh_toGrid = 0.082
panel_baseprice_per_kW = 1500


def get_peak_power(area):
    return round(area * solarRadiation * efficiency, 2)


def get_energy_output(area):
    energy_output = 0
    peak_power = get_peak_power(area)
    for k in specific_efficiency:
        energy_output += k * peak_power
    return round(energy_output, 2)


def get_yearly_revenue(area, self_consumption):
    energy_output = get_energy_output(area)
    return round(energy_output * self_consumption * price_per_kwh_ownConsumption + energy_output * (
        1 - self_consumption) * price_per_kwh_toGrid, 2)


def get_installation_fixcosts(area):
    return round(750 + area * 20, 2)


def get_inverter_costs(area):
    # Assuming that one inverter can handle up to 10kW and costs 200€
    return round(int(get_peak_power(area) / 10) * 200, 2)


def get_panel_costs_by_area(area):
    # Bulk discount function until 200kW installed capacity
    if area >= 800:
        return panel_baseprice_per_kW - 600
    return round(panel_baseprice_per_kW - ((-1) * ((area / 800) - 1) ** 2 + 1) * 600, 2)


def get_initial_investment_costs(area):
    return round(get_panel_costs_by_area(area) * get_peak_power(area) + get_installation_fixcosts(area) + get_inverter_costs(area), 2)


def get_break_even_time(area, self_consumption):
    return round(get_initial_investment_costs(area) / get_yearly_revenue(area, self_consumption), 2)


def print_info(area, self_consumption_ratio):
    print(f"Peak Power of Solar Panel System on Roof: {get_peak_power(area)} kW")
    print(f"Yearly energy Output: {get_energy_output(area)} kWh")
    print(f"Yearly revenue in Euro: Example with 25% self consumption: {round(get_yearly_revenue(area, .25), 2)}€")
    print(f"Yearly revenue in Euro: Example with 30% self consumption: {round(get_yearly_revenue(area, .3), 2)}€")
    print(f"Yearly revenue in Euro: Example with 50% self consumption: {get_yearly_revenue(area, .5)}€")
    print(f"Yearly revenue in Euro: Example with 100% self consumption: {get_yearly_revenue(area, 1)}€")
    print(f"Installation costs/Initial investment: {get_initial_investment_costs(area)}€")
    break_even_years = round(get_break_even_time(area, float(self_consumption_ratio)), 2)
    print(f"Break even with {self_consumption_ratio * 100}% self_consumption after {break_even_years} years. Yay!")
