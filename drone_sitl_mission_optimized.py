from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

print("Connecting to vehicle...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

def arm_and_takeoff(target_altitude):
    print("Arming motors...")
    while not vehicle.is_armable:
        print("Waiting for vehicle to become armable...")
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print(f"Taking off to {target_altitude} meters...")
    vehicle.simple_takeoff(target_altitude)

    while True:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt}")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Target altitude reached.")
            break
        time.sleep(1)

def go_to_waypoint(latitude, longitude, altitude):
    waypoint = LocationGlobalRelative(latitude, longitude, altitude)
    vehicle.simple_goto(waypoint)
    print(f"Going to waypoint: {latitude}, {longitude}, {altitude}")

    # Wait for the drone to reach the waypoint
    while True:
        battery_status = vehicle.battery
        if battery_status.level is not None:
            print(f"Battery level: {battery_status.level}%")
            
           
            
            if battery_status.level < 20 and battery_status.level>3:
                print(f"Low battery detected: {battery_status.level}%. Returning to launch.")
                return_to_launch()
                

        current_location = vehicle.location.global_relative_frame
        print("Current location:", current_location)

        # Check if the drone is close to the target location and altitude
        if (abs(current_location.lat - latitude) < 0.0001 and
            abs(current_location.lon - longitude) < 0.0001 and
            abs(current_location.alt - altitude) < 0.5):
            print("Reached waypoint")
            break
        time.sleep(1)

    time.sleep(10)

def return_to_launch():
    print("Returning to launch...")
    vehicle.mode = VehicleMode("RTL")
    battery_status = vehicle.battery
    print(f"Battery level: {battery_status.level}%")
    if battery_status.level < 3:
                print(f"Critical battery level detected: {battery_status.level}%. Landing immediately!")
                land_now()
              

def land_now():
    print("Landing immediately...")
    vehicle.mode = VehicleMode("LAND")
    while vehicle.armed:
        print("Waiting for the drone to land...")
        battery_status = vehicle.battery
        time.sleep(1)
    print("Drone has landed.")

try:
    arm_and_takeoff(10)

    # New waypoints close to starting position in different directions
    waypoints = [
        (-35.35878455, 149.16525118, 10),  # 500m north
        (-35.36328455, 149.17075118, 15),  # 500m east
        (-35.36778455, 149.16525118, 5),   # 500m south
        (-35.36328455, 149.15975118, 10),  # 500m west
        (-35.35878455, 149.16525118, 8),  # 500m north
    ]

    for lat, lon, alt in waypoints:
        go_to_waypoint(lat, lon, alt)

    while vehicle.mode.name != "LAND":
        print(f"Current mode: {vehicle.mode.name}")
        time.sleep(1)

    print("Landed. Mission complete.")

finally:
    print("Closing vehicle connection...")
    vehicle.close()
