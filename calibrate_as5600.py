"""
    Author: Tevin Poudrier
    Date: Thu Jul 25 11:42:37 PM MDT 2024
    Description: Get calibration factor for as5600 for any linear rail
"""

from peripherals.as5600 import as5600

encoder = as5600()

print("Linear calibration for as5600 encoder")
print("Move platform to bottom of linear rail and press enter")
input("")

print("Home set at encoder raw position: " + str(encoder.get_raw_position()))
encoder.set_home()

print("Move platform to top of linear rail and press enter")
input("")

raw_end_position = encoder.get_raw_position()
print("End set at encoder raw position: " + str(raw_end_position))

distance = float( input("Enter distance from start to end of linear rail:   "))

print("Your calibration factor is: " + str(distance/raw_end_position))
print("\t can be represented by %f/%f" % (distance,raw_end_position))