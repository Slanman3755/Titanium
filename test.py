import krpc
import time
import math

conn = krpc.connect(name = "Mission Control")

canvas = conn.ui.stock_canvas

# Get the size of the game window in pixels
screen_size = canvas.rect_transform.size

# Add a panel to contain the UI elements
panel = canvas.add_panel()

# Position the panel on the left of the screen
rect = panel.rect_transform
rect.size = (200, 50)
rect.position = (0, 0)

# Add a button to set the throttle to maximum
button = panel.add_button("Launch")
button.rect_transform.position = (0, 0)

vessel = conn.space_center.active_vessel
vessel.auto_pilot.reference_frame = vessel.surface_reference_frame

while not button.clicked:
	time.sleep(.02)
panel.visible = False

vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.target_roll = 0
vessel.control.throttle = 1
vessel.auto_pilot.engage()
print("3...")
time.sleep(1)
print("2...")
time.sleep(1)
print("1...")
time.sleep(1)
print("LIFTOFF!!!")

vessel.control.activate_next_stage()
time.sleep(.05)
vessel.control.activate_next_stage()

periapsis_altitude = 0
apoapsis_altitude = 0
target_altitude = 300000
altitude = 0
liquid_fuel_amount = 0
solid_fuel_amount = 0
boosters = False
first_stage = False
fairing = False
frame = False
circle = False
while altitude < 8000 or periapsis_altitude < target_altitude - 500:
	apoapsis_altitude = vessel.orbit.apoapsis_altitude
	periapsis_altitude = vessel.orbit.periapsis_altitude
	solid_fuel_amount = vessel.resources.amount('SolidFuel')
	liquid_fuel_amount = vessel.resources.amount('LqdHydrogen')
	altitude = vessel.flight().mean_altitude

	if solid_fuel_amount < 0.1 and not boosters:
		print("Booster Seperation...")
		vessel.control.activate_next_stage()
		boosters = True

	if liquid_fuel_amount < 18286 and not first_stage:
		print("Main Engine Seperation...")
		vessel.control.activate_next_stage()
		first_stage = True

	if altitude > 120000 and not fairing:
		print("Fairing Jettison...")
		for f in vessel.parts.fairings:
			f.jettison()
		fairing = True

	if circle or (altitude > 8000 and altitude >= apoapsis_altitude - 100):
		vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
		vessel.auto_pilot.target_direction = (0, 1, 0)
		vessel.control.throttle = 1
		circle = True

	if altitude > 8000 and altitude <= apoapsis_altitude - 50 and liquid_fuel_amount < 18286 and not circle:
		vessel.control.throttle = 0
		target_altitude = apoapsis_altitude

	if altitude > 8000 and apoapsis_altitude < target_altitude and liquid_fuel_amount >= 18286:
		vessel.control.throttle = 1
		frac = 1 - (apoapsis_altitude / target_altitude)
		vessel.auto_pilot.target_heading = 90
		vessel.auto_pilot.target_pitch = 90.0 * frac

	if apoapsis_altitude > target_altitude and liquid_fuel_amount >= 18286:
		vessel.control.throttle = 1
		frac = 1 - math.pow((1.05 * apoapsis_altitude) / target_altitude, 2)
		vessel.auto_pilot.target_heading = 90
		vessel.auto_pilot.target_pitch = 90.0 * frac

	time.sleep(.01)

print("Orbit Achieved")
vessel.auto_pilot.disengage()
vessel.control.throttle = 0