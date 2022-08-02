#!/usr/bin/env python3
from eye import *

# 06-followers.py - FOLLOWER

angular_base_speed = 45  # initial angular BASE speed in degrees per second, i.e. deg/s. For use in Proportional!
angular_speed = 0  # initial angular speed in degrees per second, i.e. deg/s.
angular_error = 0  # initial angular error. For use in Proportional!

# follower would usually run a bit slower than leader
linear_speed = 200  # initial speed in millimeter per second, i.e. mm/s. Later maybe change to Proportional!

max_range = 15000  # the maximum range (distance) that the robot can sense/see, e.g. 15000 mm is 15 meters

LCDMenu("SCAN", "", "", "END")

while True:
    LCDClear()
    min_scan = max_range  # put a very high scan value (distance) initially at each step/scan, 15000 mm is 15 meters
    min_scan_index = 0  # initial (at each step/scan) index is 0, i.e. rear of robot
    heading_to_turn = 0  # initial (at each step/scan) heading to turn is 0 degree, i.e. no need to turn!

    LCDMenu("SCAN", "", "", "END")
    LCDSetPrintf(1, 45, "06-followers.py - FOLLOWER")

    scan = LIDARGet()

    # NOTE: A FORWARD-facing robot, i.e. 90 to 270 scan index only
    # for i in range(90, 270):  # ALTERNATIVE: read only the front-side of the robot
    for i in range(90, 270):  # read only within the front range around the robot
        LCDLine(i, 250 - int(scan[i] / 10), i, 250, BLUE)
        if scan[i] <= min_scan:
            LCDSetPrintf(
                2, 45, "NEW min detected: %d mm", scan[i]
            )  # just to check the minimum reading
            min_scan = scan[i]
            min_scan_index = i

    # mark the minimum reading on the plot, using yellow line
    LCDLine(min_scan_index, 250 - int(min_scan / 10), min_scan_index, 250, YELLOW)

    LCDLine(180, 0, 180, 250, RED)  # straight, 0 degrees
    LCDLine(90, 0, 90, 250, GREEN)  # left, -90 degrees
    LCDLine(270, 0, 270, 250, GREEN)  # right, +90 degrees
    LCDSetPrintf(19, 0, "            -90             0             +90")

    # Find true heading here!
    # robot will turn towards the minimum distance sensed
    # emulating a Predator (sub)behavior
    #
    # HINT: play around using the Can to see the behavior
    # i.e. putting it near around the robot, to make it turn
    if min_scan_index == 180:  # heading is exactly at front!
        heading_to_turn = 0
    elif min_scan_index < 180:
        heading_to_turn = 180 - min_scan_index
        heading_to_turn = heading_to_turn * 1  # turn left, +ve angle
    elif min_scan_index > 180:
        heading_to_turn = min_scan_index - 180
        heading_to_turn = heading_to_turn * -1  # turn right, -ve angle
    else:  # error? remain heading 0
        heading_to_turn = 0

    # just checking if min_scan actually has the minimum distance scanned
    if min_scan == min(scan):
        LCDSetPrintf(3, 45, "LIDAR min dist scanned: %d mm", min_scan)
        LCDSetPrintf(4, 45, "LIDAR index of min dist: %d", min_scan_index)
        LCDSetPrintf(5, 45, "Heading to turn: %d degrees", heading_to_turn)

    # DONE:
    # Proportional turn: the further the heading to turn,
    # the faster the angular speed should be, vice-versa.
    angular_error = abs(heading_to_turn) - angular_base_speed
    angular_speed = angular_error + angular_base_speed    
      
    if min_scan < max_range:  # something is within detectable range
        LCDSetPrintf(6, 45, "Something detected!")
        
        if heading_to_turn != 0: # only turn if the heading to turn is NOT right in-front!
            VWTurn(
                heading_to_turn, angular_speed
            )  # angular_speed should be Proportional, now!
            VWWait()  # OPTIONAL: can remove for this scenario, for now        

        # RE-INIT angular variables
        angular_error = 0
        angular_speed = 0

        # move straight forward, as far as the minimum distance scanned.
        VWStraight(
            min_scan, linear_speed
        )  # linear_speed should be Proportional, later!
        # VWWait()  # OPTIONAL: can remove for this scenario, for now
    else:  # NOTHING is within detectable range
        LCDSetPrintf(6, 45, "Something NOT detected!")
        VWSetSpeed(0, 0)  # just stay put, i.e. Stop!