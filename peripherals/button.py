"""
    Author: Tevin Poudrier
    Date: Thu Jul 25 03:34:53 PM MDT 2024
    Description: Driver for GPIO button on RPI 4 with pull-up resistor
"""
import RPi.GPIO as GPIO
import time

if __name__ == "__main__":
    from RepeatTimer import RepeatTimer
else:
    from peripherals.RepeatTimer import RepeatTimer

class button():
        
    def __init__(self, pin):

        #Initialize GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #initalize variables
        self.channel = pin
        self.__button_state__ = True
        self.__prev_state__ = True
        self.__prev_time__ = time.time()

        #initalize callbakcs
        self.__callback_rise_fall__ = None
        self.__callback_rising__ = None
        self.__callback_falling__ = None
        self.debounce = 50/1000 #ms
        
        #start timer, updates position buffer every 10ms
        self.timer = RepeatTimer(0.01, self.__poll_button__)
        self.timer.start()

    def set_callbacks(self, rise_fall = None, rising = None, falling = None):
        """
        Set the function that is called on a button edge.
        rise_fall triggers on both rising and falling edge.
        falling triggers on falling edge (button pressed).
        rising triggers on rising edge (button released).
        """
        self.__callback_falling__ = falling
        self.__callback_rise_fall__ = rise_fall
        self.__callback_rising__ = rising
    
    def __poll_button__(self):
        """
        Read the current value of the button and trigger callbacks when button is pressed.
        Needs to be called constantly to catch button edges
        """
        self.__button_state__ = GPIO.input(self.channel)

        #Detect button state changed with debounce
        if (self.__button_state__ != self.__prev_state__ and (time.time() - self.__prev_time__) > self.debounce ):
            
            #Trigger rising and falling edge callback
            if(self.__callback_rise_fall__ != None):
                self.__callback_rise_fall__() 
            
            #Trigger rising edge callback
            if(self.__callback_rising__ != None and self.__button_state__ == True and self.__prev_state__ == False):
                self.__callback_rising__()

            #Trigger falling edge callbackj
            if(self.__callback_falling__ != None and self.__button_state__ == False and self.__prev_state__ == True):
                self.__callback_falling__()

            #Store debounce info
            self.__prev_state__ = self.__button_state__
            self.__prev_time__ = time.time()

    def close (self):
        """
        Release resources
        """
        self.timer.cancel()


if __name__ == "__main__":
    count = 0
    def mu_callback():
        global count
        count += 1
        print("pressed: " + str(count))

    count2 = 0
    def mu_callback2():
        global count2
        count2 += 1
        print("released: " + str(count2))

    my_button = button(pin=7)
    my_button.set_callbacks(falling=mu_callback, rising=mu_callback2)

    while (True):
        pass

