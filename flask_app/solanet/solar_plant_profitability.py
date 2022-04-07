"""This module provides profitability calculations for deciding
whether to install a solar power plant on top of a given house."""

from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np


@dataclass
class SolarPlant:
    """Representing the profitability properties of a solar plant,
    given the plant's surface area and self-consumption rate."""

    # plant-specific parameters the plant owner can adjust
    area: float
    self_consumption: float

    # physics / solar market parameters used for the calculations
    solar_radiation: float=1
    efficiency: float=.25
    efficiency_by_month: List[float] = field(default_factory=lambda: \
        [26, 59, 72, 128, 124, 155, 131, 123, 89, 63, 27, 21])
    price_per_kwh_own_consumption: float = 0.3
    price_per_kwh_to_grid: float = 0.082
    panel_baseprice_per_kw: float = 1500

    @property
    def peak_power(self) -> float:
        """The solar plant's peak power (in kWh)."""
        return round(self.area * self.solar_radiation * self.efficiency, 2)

    @property
    def energy_output(self) -> float:
        """The solar plant's energy output (in kWh)."""
        return round(sum([k * self.peak_power for k in self.efficiency_by_month]), 2)

    @property
    def yearly_revenue(self):
        """The solar plant's yearly revenue (in Euro)."""
        energy_output = self.energy_output
        return round(energy_output * self.self_consumption * self.price_per_kwh_own_consumption + \
                     energy_output * (1 - self.self_consumption) * self.price_per_kwh_to_grid, 2)

    @property
    def installation_fixcosts(self):
        """The solar plant's installation fixcosts (in Euro)."""
        return round(750 + self.area * 20, 2)

    @property
    def inverter_costs(self):
        """The solar plant's costs for buying an inverter (in Euro)."""
        # Assuming that one inverter can handle up to 10kW and costs 200€
        return round(int(self.peak_power / 10) * 200, 2)

    @property
    def panel_costs_by_area(self):
        """The solar plant's cost for buying a solar panels, considering bulk discount (in Euro)."""
        # Bulk discount function until 200kW installed capacity
        if self.area >= 800:
            return self.panel_baseprice_per_kw - 600
        bulk_discount = ((-1) * ((self.area / 800) - 1) ** 2 + 1) * 600
        return round(self.panel_baseprice_per_kw - bulk_discount, 2)

    @property
    def initial_investment_costs(self):
        """The solar plant's overall initial investment costs (in Euro)."""
        return round(self.panel_costs_by_area * self.peak_power + \
                     self.installation_fixcosts + self.inverter_costs, 2)

    @property
    def break_even_years(self):
        """The solar plant's break-even point in terms of profitability (in years)."""
        return round(self.initial_investment_costs / self.yearly_revenue, 2)


@dataclass
class SolarPlantEvaluation:
    """Representing an evaluation of an entire solar plant,
    considering the given rooftop surface area and different
    assumptions on the amount of self-consumption."""

    area: float
    self_consumption_ratios: List[int] = field(default_factory=lambda: list(range(101)), init=False)
    plants_by_sc: Dict[int, SolarPlant] = field(init=False)

    def __post_init__(self):
        self.plants_by_sc = {sc_ratio: SolarPlant(self.area, sc_ratio)
                             for sc_ratio in self.self_consumption_ratios}

    @property
    def common(self) -> SolarPlant:
        """Yielding a solar plant instance, representing common properties
        that are not related to the self-consumption rate."""
        first_key = list(self.plants_by_sc.keys())[0]
        return self.plants_by_sc[first_key]

    def __str__(self) -> str:
        break_even_years = [round(self.plants_by_sc[sc].break_even_years, 2)
                            for sc in self.self_consumption_ratios]
        min_id, max_id = np.argmin(break_even_years), np.argmax(break_even_years)
        min_years, max_years = break_even_years[min_id], break_even_years[max_id]
        roi = round((20 - min_years) * self.plants_by_sc[min_id].yearly_revenue, 2)

        yearly_revenue_25 = self.plants_by_sc[25].yearly_revenue
        yearly_revenue_30 = self.plants_by_sc[30].yearly_revenue
        yearly_revenue_50 = self.plants_by_sc[50].yearly_revenue
        yearly_revenue_100 = self.plants_by_sc[100].yearly_revenue

        out  = f"Peak Power of Solar Panel System on Roof: {self.common.peak_power} kW."
        out += f"Yearly energy Output: {self.common.energy_output} kWh."
        out += f"Yearly revenue with 25% self-consumption: {yearly_revenue_25:.2f} €."
        out += f"Yearly revenue with 30% self-consumption: {yearly_revenue_30:.2f} €."
        out += f"Yearly revenue with 50% self-consumption: {yearly_revenue_50:.2f} €."
        out += f"Yearly revenue with 100% self-consumption: {yearly_revenue_100:.2f} €."
        out += f"Installation costs/Initial investment: {self.common.initial_investment_costs} €."
        out += f"Break even within {min_years} to {max_years} years."
        out += f'Possible return on investment, assuming a plant lifetime of 20 years is {roi}.'
        return out

    def __repr__(self) -> str:
        return self.__str__()
