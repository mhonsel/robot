def uni_to_diff(v, omega, R, T):
    # v = translational velocity (m/s)
    # omega = angular velocity (rad/s)
    # R = wheel radius
    # T = wheel track

    v_l = (v - (T / 2.0) * omega) / R
    v_r = (v + (T / 2.0) * omega) / R
#    v_l = ((2.0 * v) - (omega * T)) / (2.0 * R)
#    v_r = ((2.0 * v) + (omega * T)) / (2.0 * R)

    return v_l, v_r

def diff_to_uni(v_l, v_r, R, T):
    # v_l = left-wheel angular velocity (rad/s)
    # v_r = right-wheel angular velocity (rad/s)
    # R = wheel radius
    # T = wheel track

    v = (R / 2.0) * (v_r + v_l)
    omega = (R / T) * (v_r - v_l)

    return v, omega
