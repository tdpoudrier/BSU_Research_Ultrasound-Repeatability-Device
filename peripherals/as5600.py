"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: Driver for as5600 encoder, uses a timer to get consistant data
"""
import smbus2
import time

if __name__ == "__main__":
    from RepeatTimer import RepeatTimer
else:
    from peripherals.RepeatTimer import RepeatTimer

class as5600(object):
    """
    Encoder object, must be closed when done using
    """

    def __init__(self, linear_calibration = 1):
        """
        Connect to as5600, start polling timer, and set home. Define linear_calibration for accurate linear position. 
        Run calibrate_as5600.py to get calibration factor
        """
        self.bus = smbus2.SMBus(1)

        self.ADDRESS = 0x36

        self.ext_angle = 2048
        self.position = 0
        self.home = 0

        self.linear_calibration_factor = linear_calibration
        
        self.set_home()
        
        #start timer, updates position buffer every 10ms
        self.timer = RepeatTimer(0.01, self.__update_buffer__)
        self.timer.start()

    def ReadRawAngle(self):
        """
        Get the binary angular position data from as5600
        """
        read_bytes = self.bus.read_i2c_block_data(self.ADDRESS, 0x0C, 2) #read 2 bytes from as5600 register 0x0C
        return (read_bytes[0]<<8) | read_bytes[1]

    def get_degrees(self):
        """
        Get the current angular position in degrees
        """
        bytes = self.ReadRawAngle()
        return bytes * 360/4096

    def ReadMagnitude(self):
        read_bytes = self.bus.read_i2c_block_data(self.ADDRESS, 0x1B, 2) #read 2 bytes from as5600 register 0x1B
        return (read_bytes[0]<<8) | read_bytes[1]

    def get_raw_position(self):
        """
        Get binary representation of postion
        """
        return self.position
    
    def get_position(self):
        """
        Get the current linear position of the as5600 from the buffer in inches
        """
        return self.position * self.linear_calibration_factor

    def set_home(self):
        """
        Set the starting point for linear position calculations
        """
        self.home = self.__linear_position__()
    
    def close(self):
        """
        Stop the timer and release resources
        """
        self.timer.cancel()
    
    def __linear_position__(self):
        """
        Calculate the linear position of the encoder
        """
        
        #Calculate change in angle, prevent bit wrap around, assumes encoder did not rotate more and 180 degrees
        delta = (self.ReadRawAngle() - self.ext_angle) % 4095
        if delta > 2048:
            delta -= 4095

        #Add change to current
        self.ext_angle = self.ext_angle+delta

        #calculate position
        position = self.ext_angle

        return position - self.home
    
    def __update_buffer__(self):
        """
        Store the linear position in the buffer
        """
        self.position = self.__linear_position__()



if __name__ == "__main__":
    encoder = as5600()
    while (True):
        position = encoder.get_position()
        raw_pos = encoder.get_raw_position()
        print("Pos: %s, raw: %s" % (position, raw_pos))
        time.sleep(1)