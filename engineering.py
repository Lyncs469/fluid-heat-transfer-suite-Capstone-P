"""Reusable engineering calculations for the PE 262 capstone application.

The module contains object-oriented models for fluids and pipes plus a utility
class for heat-transfer calculations.  The Streamlit pages import these
classes so that engineering logic is separated from the user interface.
"""

import numpy as np


class Fluid:
    """Represent a fluid using density and dynamic viscosity."""

    PRESETS = {
        "Water (20°C)": {"rho": 998.0, "mu": 1.002e-3},
        "Air (20°C)": {"rho": 1.204, "mu": 1.825e-5},
        "Crude Oil (20°C)": {"rho": 870.0, "mu": 0.010},
    }

    def __init__(self, name="Water (20°C)", rho=None, mu=None):
        """Create a fluid from a preset or user-supplied properties.

        Args:
            name: Fluid name.
            rho: Density in kg/m³ for a user-defined fluid.
            mu: Dynamic viscosity in Pa·s for a user-defined fluid.

        Raises:
            ValueError: If required custom properties are missing or invalid.
        """
        self.name = name
        if name in self.PRESETS and rho is None and mu is None:
            self.rho = self.PRESETS[name]["rho"]
            self.mu = self.PRESETS[name]["mu"]
            return

        if rho is None or mu is None:
            raise ValueError("A user-defined fluid requires both density and viscosity.")
        if rho <= 0 or mu <= 0:
            raise ValueError("Density and viscosity must be positive.")
        self.rho = float(rho)
        self.mu = float(mu)

    def __repr__(self):
        """Return a concise representation of the fluid object."""
        return f"Fluid({self.name!r}, rho={self.rho} kg/m³, mu={self.mu} Pa·s)"


class Pipe:
    """Represent a circular pipe and perform internal-flow calculations."""

    def __init__(self, diameter_m, length_m, roughness_m=0.0):
        """Create a pipe.

        Args:
            diameter_m: Internal diameter in metres; must be positive.
            length_m: Pipe length in metres; must be positive.
            roughness_m: Absolute roughness in metres; must be non-negative.

        Raises:
            ValueError: If a supplied pipe dimension is non-physical.
        """
        if diameter_m <= 0:
            raise ValueError("Pipe diameter must be positive.")
        if length_m <= 0:
            raise ValueError("Pipe length must be positive.")
        if roughness_m < 0:
            raise ValueError("Roughness cannot be negative.")
        self.D = float(diameter_m)
        self.L = float(length_m)
        self.eps = float(roughness_m)

    def area(self):
        """Return the pipe cross-sectional area in m²."""
        return np.pi * self.D**2 / 4.0

    def velocity_from_flowrate(self, Q):
        """Return mean velocity in m/s from flow rate Q in m³/s."""
        if Q < 0:
            raise ValueError("Flow rate cannot be negative.")
        return Q / self.area()

    def reynolds_number(self, fluid, velocity):
        """Return Reynolds number from fluid properties and mean velocity."""
        if velocity < 0:
            raise ValueError("Velocity cannot be negative.")
        return fluid.rho * velocity * self.D / fluid.mu

    @staticmethod
    def flow_regime(Re):
        """Classify internal pipe flow as laminar, transitional, or turbulent."""
        if Re < 2300:
            return "Laminar"
        if Re < 4000:
            return "Transitional"
        return "Turbulent"

    def friction_factor(self, Re):
        """Return the Darcy friction factor for the supplied Reynolds number.

        Laminar flow uses the exact relation f = 64/Re.  Turbulent flow uses
        the explicit Swamee–Jain approximation to the Colebrook equation.
        In the transitional range, a simple linear interpolation between the
        laminar value at Re=2300 and the turbulent estimate at Re=4000 is used.
        This is an engineering approximation because transitional flow does
        not have one universally accepted explicit friction-factor equation.
        """
        if Re <= 0:
            return np.nan

        relative_roughness = self.eps / self.D

        def turbulent_factor(reynolds):
            """Calculate the Swamee–Jain turbulent Darcy friction factor."""
            return 0.25 / (
                np.log10(relative_roughness / 3.7 + 5.74 / reynolds**0.9)
            ) ** 2

        if Re < 2300:
            return 64.0 / Re
        if Re < 4000:
            f_2300 = 64.0 / 2300.0
            f_4000 = turbulent_factor(4000.0)
            fraction = (Re - 2300.0) / (4000.0 - 2300.0)
            return f_2300 + fraction * (f_4000 - f_2300)
        return turbulent_factor(Re)

    def pressure_drop(self, fluid, velocity):
        """Return Darcy-Weisbach pressure drop in Pa over the pipe length."""
        if velocity < 0:
            raise ValueError("Velocity cannot be negative.")
        if velocity == 0:
            return 0.0

        Re = self.reynolds_number(fluid, velocity)
        f = self.friction_factor(Re)
        return f * (self.L / self.D) * (fluid.rho * velocity**2 / 2.0)


class HeatTransfer:
    """Provide stateless conduction and Newton-cooling calculations."""

    @staticmethod
    def conduction_flat_wall(k, A, thickness, T_hot, T_cold):
        """Calculate steady 1-D heat-transfer rate through a flat wall.

        Fourier's law is Q = k A (T_hot - T_cold) / L.
        """
        if k <= 0 or A <= 0 or thickness <= 0:
            raise ValueError("Thermal conductivity, area, and thickness must be positive.")
        return k * A * (T_hot - T_cold) / thickness

    @staticmethod
    def cooling_time(T0, T_target, T_inf, h, A, m, cp):
        """Calculate time in seconds to reach a valid target temperature.

        Newton's law gives T(t)=T_inf+(T0-T_inf)exp[-hAt/(mcp)].
        The target must lie strictly between T0 and T_inf.
        """
        if h <= 0 or A <= 0 or m <= 0 or cp <= 0:
            raise ValueError("h, A, mass, and cp must all be positive.")
        if T0 == T_inf:
            raise ValueError("Initial temperature cannot equal ambient temperature.")

        ratio = (T_target - T_inf) / (T0 - T_inf)
        if not 0 < ratio < 1:
            raise ValueError(
                "Target temperature must lie strictly between the initial and ambient temperatures."
            )

        k_const = h * A / (m * cp)
        return -np.log(ratio) / k_const

    @staticmethod
    def cooling_curve(T0, T_inf, h, A, m, cp, t_max, n_points=200):
        """Generate time and temperature arrays for Newtonian cooling."""
        if h <= 0 or A <= 0 or m <= 0 or cp <= 0:
            raise ValueError("h, A, mass, and cp must all be positive.")
        if t_max <= 0:
            raise ValueError("Maximum curve time must be positive.")
        if n_points < 2:
            raise ValueError("At least two curve points are required.")

        k_const = h * A / (m * cp)
        t = np.linspace(0, t_max, int(n_points))
        temperature = T_inf + (T0 - T_inf) * np.exp(-k_const * t)
        return t, temperature
