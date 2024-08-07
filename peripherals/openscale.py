import serial
import time

from peripherals.RepeatTimer import RepeatTimer


'''
Openscale is configured to be in continuous mode and samples are sent every 50ms
data formate is: timestamp, data, unit,
'''
class openscale(object):
    '''
    Get force on load cell from openscale development board over usb (ttyUSB0)
    '''

    port = '/dev/ttyUSB0'
    BAUDRATE = 115200

    serial_port = serial.Serial(port, BAUDRATE, timeout=0.1)

    def __init__ (self):
        time.sleep(2) #wait for inital messages to be sent

        self.__force_buffer__ = 0

        #Start repeat timer, update force buffer every 60ms
        self.timer = RepeatTimer(0.06, self.__update_buffer__)
        self.timer.start() 

    
    def get_binary (self) -> bytes:
        '''
        get binary line of data from openscale over usb
        '''
        #clear buffer
        self.serial_port.reset_input_buffer()

        #loop till line is read from openscale
        data = b''
        while (data == b''):
            data = self.serial_port.readline()

            # Verify data
            # valid data has 3 commas (timestamp, weight, unit,)
            if ( (data.count(b',') == 3) and (data != None) ):
                return bytes(data)

    def get_line (self) -> list[str]:
        '''
        returns iterable string representation of openscale data
        '''        

        #Sometimes none is returned, prevent by calling method again
        while (True):
            data_line = self.get_binary()
            if (data_line != None): 
                break
        
        #convert to string
        data_line = data_line.decode('utf-8')

        #convert to iterable list
        data_list = data_line.split(',')

        return data_list
    
    def get_force (self) -> float:
        '''
        returns force on scale as a float
        '''
        return self.__force_buffer__
    
    def get_unit (self) -> str:
        '''
        get the current unit
        '''
        data_list = self.get_line()        
        return data_list[2]
    
    def close (self):
        """
        Release resources
        """
        self.timer.cancel()
    
    def __update_buffer__(self):
        """
        Get newest measurement and store in buffer
        """
        data_list = self.get_line()        
        self.__force_buffer__ = float(data_list[1])


if __name__ == "__main__":
    weight_sensor = openscale()
    times = []
    
    while True:
        start_bin = time.time()
        binary = weight_sensor.get_binary()
        end_bin = time.time()
        
        start = time.time()
        mass = weight_sensor.get_force()
        end = time.time()
        # print(str(mass) + "kg, " + str(end-start) + " seconds")
        print("%s kg, %.3f seconds, binary %.3f seconds" % (mass, (end-start), (end_bin - start_bin)))

        times.append((end-start))

        if (len(times) >= 10):
            average = sum(times) / len(times)
            print("\tAverage time for 10 samples is %.3f seconds" % (average))
            print("\tTotal time: %.3f" % sum(times))
            times.clear()
            time.sleep(2)
        
        # print(weight_sensor.get_binary())
        # time.sleep(0.1)