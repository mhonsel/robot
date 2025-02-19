def uni_to_diff(v: float, omega: float, R: float, T: float) -> tuple[float, float]:
    """
    Converts **unicycle model velocities** (linear and angular) to **differential drive velocities**.

    Args:
        v (float): Translational velocity (m/s).
        omega (float): Angular velocity (rad/s).
        R (float): Wheel radius (m).
        T (float): Wheel track (distance between wheels, m).

    Returns:
        tuple[float, float]: Left and right wheel velocities (rad/s).
    """
    # Compute the left and right wheel velocities based on the unicycle model
    v_l = (v - (T / 2.0) * omega) / R  # Left wheel velocity (rad/s)
    v_r = (v + (T / 2.0) * omega) / R  # Right wheel velocity (rad/s)

    return v_l, v_r


def diff_to_uni(v_l: float, v_r: float, R: float, T: float) -> tuple[float, float]:
    """
    Converts **differential drive velocities** (wheel speeds) back to **unicycle model velocities**.

    Args:
        v_l (float): Left-wheel angular velocity (rad/s).
        v_r (float): Right-wheel angular velocity (rad/s).
        R (float): Wheel radius (m).
        T (float): Wheel track (distance between wheels, m).

    Returns:
        tuple[float, float]: Translational velocity (m/s) and angular velocity (rad/s).
    """
    # Compute translational and angular velocity from left and right wheel speeds
    v = (R / 2.0) * (v_r + v_l)  # Translational velocity (m/s)
    omega = (R / T) * (v_r - v_l)  # Angular velocity (rad/s)

    return v, omega