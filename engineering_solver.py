
import math

G = 9.80665

def positive(name, value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(name + " must be a finite positive number")
    return value

def simply_supported_beam(P, L, E, I, c):
    """Central point load on a simply supported beam.
    SI units: N, m, Pa, m^4, m.
    """
    P = positive("P", P)
    L = positive("L", L)
    E = positive("E", E)
    I = positive("I", I)
    c = positive("c", c)

    moment = P * L / 4
    deflection = P * L**3 / (48 * E * I)
    stress = moment * c / I

    return {
        "maximum_moment_Nm": moment,
        "maximum_deflection_m": deflection,
        "maximum_bending_stress_Pa": stress,
        "assumption": "Central point load; linear elastic Euler-Bernoulli beam."
    }

def concrete_volume(length, width, thickness):
    """Concrete volume and estimated mass using 2400 kg/m^3."""
    L = positive("length", length)
    W = positive("width", width)
    H = positive("thickness", thickness)

    volume = L * W * H
    density = 2400.0
    mass = volume * density
    weight = mass * G

    return {
        "volume_m3": volume,
        "estimated_mass_kg": mass,
        "estimated_weight_N": weight,
        "density_kg_m3": density,
        "assumption": "Normal-weight concrete density assumed as 2400 kg/m3."
    }

def axial_stress(force, area):
    """Axial stress = force / cross-sectional area."""
    F = float(force)
    if not math.isfinite(F):
        raise ValueError("force must be finite")
    A = positive("area", area)

    return {
        "axial_stress_Pa": F / A,
        "axial_stress_MPa": F / A / 1e6,
        "assumption": "Uniform axial stress; eccentricity and buckling ignored."
    }

def mechanical_torque(power_watts, rpm):
    """Torque = power / angular velocity."""
    power = positive("power_watts", power_watts)
    speed = positive("rpm", rpm)

    omega = 2 * math.pi * speed / 60
    torque = power / omega

    return {
        "angular_velocity_rad_s": omega,
        "torque_Nm": torque,
        "power_W": power
    }

def electrical_ohms(voltage, current):
    """DC Ohm's law and electrical power."""
    V = float(voltage)
    I = float(current)

    if not math.isfinite(V) or not math.isfinite(I):
        raise ValueError("Voltage and current must be finite")
    if I == 0:
        raise ValueError("Current cannot be zero when calculating resistance")

    resistance = V / I
    power = V * I

    return {
        "resistance_ohm": resistance,
        "power_W": power,
        "voltage_V": V,
        "current_A": I,
        "assumption": "DC circuit; ideal Ohm's law."
    }

def solve(task, **kwargs):
    methods = {
        "beam": simply_supported_beam,
        "concrete": concrete_volume,
        "axial_stress": axial_stress,
        "torque": mechanical_torque,
        "electrical": electrical_ohms
    }

    if task not in methods:
        raise ValueError(
            "Unknown task. Available: " + ", ".join(methods)
        )

    return methods[task](**kwargs)
