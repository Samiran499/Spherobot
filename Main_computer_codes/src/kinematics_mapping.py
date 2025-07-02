import numpy as np

# Define angles in DEGREES
alpha_deg = 60   # Motor 1 angle
beta_deg = 180     # Motor 2 angle
gamma_deg = 300    # Motor 3 angle
delta_deg = 45    # Angle between motor axis & sphere surface normal

# Convert to radians
alpha = np.radians(alpha_deg)
beta  = np.radians(beta_deg)
gamma = np.radians(gamma_deg)
delta = np.radians(delta_deg)

# Radius of sphere and wheels (can be real or relative units as only ratio is required)
rs = 25
rw = 5.8

# Precompute trig values
cos_a = np.cos(alpha)
sin_a = np.sin(alpha)
cos_b = np.cos(beta)
sin_b = np.sin(beta)
cos_g = np.cos(gamma)
sin_d = np.sin(delta)
cos_d = np.cos(delta)

# Kinematic transfer matrix
T = np.array([
    [
        np.sqrt(1 - (cos_d**2 * cos_a**2)) * cos_a,
        np.sqrt(1 - (cos_d**2 * sin_a**2)) * sin_a,
        cos_d
    ],
    [
        np.sqrt(1 - (cos_d**2 * cos_b**2)) * cos_b,
        np.sqrt(1 - (cos_d**2 * sin_b**2)) * sin_b,
        cos_d
    ],
    [
        0,
        sin_d * cos_g,
        cos_d
    ]
])

# Scale matrix with radius ratio
T = (rs / rw) * T

# Display results
print("Kinematic transfer matrix (T):\n", T)

def map_speed(roll_rate=0, pitch_rate=0, yaw_rate=0):
    omega_body = np.array([pitch_rate, roll_rate, yaw_rate]).T
    omega_wheels = np.matmul(T, omega_body).T
    # print("Input angular velocity [ωx, ωy, ωz]:", omega_body)
    # print("Output wheel speeds [ω1, ω2, ω3]:", omega_wheels)
    return omega_wheels[0], omega_wheels[1], omega_wheels[2]