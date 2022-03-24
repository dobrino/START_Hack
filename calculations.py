solarRadiation = 1
efficiency = .25
specific_efficiency = [26,59,72,128,124,155,131,123,89,63,27,21]
price_per_kwh_ownConsumption = 0.3
price_per_kwh_toGrid = 0.082
panel_baseprice_per_kW = 1500

def get_peak_power(area):
    return area * solarRadiation * efficiency;

def get_energy_output(area):
    energy_output = 0
    peak_power = get_peak_power(area)
    for k in specific_efficiency:
        energy_output += k * peak_power
    return energy_output

def get_yearly_revenue(area, self_consumption):
    energy_output = get_energy_output(area)
    return energy_output * self_consumption * price_per_kwh_ownConsumption + energy_output * (1-self_consumption) * price_per_kwh_toGrid

def get_installation_fixcosts(area):
    return 750 + area * 20

def get_inverter_costs(area):
    # Assuming that one inverter can handle up to 10kW and costs 200€
    return int(get_peak_power(area) / 10) * 200

def get_initial_investment_costs(area):
    return panel_baseprice_per_kW * get_peak_power(area) + get_installation_fixcosts(area) + get_inverter_costs(area)

def get_break_even_time(area, self_consumption):
    return get_initial_investment_costs(area) / get_yearly_revenue(area, self_consumption)

def main():
    area = 400
    self_consumption_ratio = .5 # input("Enter predicted self_need ratio: ")

    print(f"Peak Power of Solar Panel Systme on Roof: {get_peak_power(area)} kW")
    print(f"Yearly energy Output: {get_energy_output(area)} kWh")
    print(f"Yearly revenue in Euro: Example with 25% self consumption: {round(get_yearly_revenue(area, .25),2)}€")
    print(f"Yearly revenue in Euro: Example with 30% self consumption: {round(get_yearly_revenue(area, .3),2)}€")
    print(f"Yearly revenue in Euro: Example with 50% self consumption: {get_yearly_revenue(area, .5)}€")
    print(f"Yearly revenue in Euro: Example with 100% self consumption: {get_yearly_revenue(area, 1)}€")
    print(f"Installation costs/Initial investment with {self_consumption_ratio * 100}% self_consumption: {get_initial_investment_costs(area)}€")
    print(f"Break even after {round(get_break_even_time(area, float(self_consumption_ratio)), 2)} years. Yay!")


if __name__ == "__main__":
    main()
