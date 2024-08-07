"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: tkinter widget for displaying error to the user with a moving bar
""" 
from tkinter import *
from tkinter import ttk

from peripherals.as5600 import as5600
from peripherals.openscale import openscale

class tk_indicator(Frame):
    '''
    Uses tkinter to create an indicator bar to display the error/difference between the target value and the current value.
    '''
    __error_margin__ = 10
    __sensitivity__ = 50

    
    def __init__(self, parent, width, height, box_size) -> None:
        '''
        Set the tkinter root and define the size of the progress bar
        Uses tkinter to create an indicator bar to display the error/difference between the target value and the current value.
        '''
        Frame.__init__(self,parent)
        
        #Create widgets
        self.canvas = Canvas(self, width=width, height=height, bg='white')
        self.low_label = ttk.Label(self, text="Low default")
        self.high_label = ttk.Label(self, text="High default")

        #Calculate center coordinates for box
        origin = width/2
        box_start_coords = (origin-box_size, 0)
        box_end_coords = (origin+box_size, height)

        #Set dimensions
        self.width = width
        self.height = height
        self.box_size = box_size

        #create error margin display
        self.canvas.config(bg='grey')
        self.error_rect = self.canvas.create_rectangle(box_start_coords,box_end_coords, fill='white')
        self.display_error_margin()
        
        #create center box for user alignment
        self.canvas.create_rectangle(box_start_coords,box_end_coords, fill='light grey')
        
        #create moving box
        self.rect = self.canvas.create_rectangle(box_start_coords,box_end_coords, fill='green')

        #layout
        self.low_label.grid(column=0, row=0)
        self.high_label.grid(column=4, row=0)
        self.canvas.grid(row=1, columnspan=5)
    
    def set_error_margin(self, new_margin):
        """
        Set the error margin of the indicator bar.
        """
        self.__error_margin__ = new_margin
        self.display_error_margin()
    
    def set_UI_sensitivity(self, new_sensitivity):
        """
        Set the ui sensitivity of the indicator bar. Defines how many error margins are displayed. Controls the size of the white/valid area
        """
        self.__sensitivity__ = new_sensitivity
        self.display_error_margin()

    def config_labels(self, left_text='Low default', right_text="High default", fontsize=10):
        """
        Set the text and fontsize of the labels above the indicator bar
        """
        self.low_label.config(text=left_text, font=("Arial",fontsize))
        self.high_label.config(text=right_text, font=("Arial", fontsize))

    def display_error_margin(self):
        """
        Show the white area of the indicator bar
        """

        #Calculate box location
        origin = self.width/2
        box_shift = (1 * self.__sensitivity__)
        box_start_coords = origin - self.box_size - box_shift

        box_shift = (-1 * self.__sensitivity__)
        box_end_coords = origin + self.box_size - box_shift

        #Move and resize box to new position on canvas
        self.canvas.coords(self.error_rect, box_start_coords, 0, box_end_coords, self.height)
    
    def update(self, new_value, target_value) -> None:
        '''
        Calculate the error between the new value and the target value
        then display it to the user
        '''
        max = self.width
        min = 0
        origin = self.width/2

        #Calculate error
        error = target_value - new_value
        num_error_margin_off = error / self.__error_margin__

        #Calculate box location
        box_shift = (num_error_margin_off * self.__sensitivity__)
        box_start_coords = origin - self.box_size - box_shift
        box_end_coords = origin + self.box_size - box_shift

        #Prevent box from moving off of canvas
        if (box_start_coords < min):
            box_start_coords = min
            box_end_coords = min + self.box_size
        if (box_end_coords > max):
            box_end_coords = max
            box_start_coords = max - self.box_size

        #Change color of box if error is greater then 1 error margin
        if ((num_error_margin_off <= 1) and (num_error_margin_off >= -1) ):
            self.canvas.itemconfig(self.rect, fill='green')
        else:
            self.canvas.itemconfig(self.rect, fill='red')
        
        #set new box location
        self.canvas.coords(self.rect, box_start_coords, 0, box_end_coords, self.height)

def move_box():
    indicator.update(sensor.linear_position(), -10)
    indicator2.update(weight_sensor.get_force(), 2.5)
    print(sensor.linear_position())
    root.after(1,move_box)

if __name__ == '__main__':
    sensor = as5600()
    weight_sensor = openscale()

    root = Tk()

    root.title("Canvas Demo")

    root.after(1,move_box)

    indicator = tk_indicator(root, 300,100, 10)
    indicator.set_error_margin(0.3)
    indicator.set_UI_sensitivity(25)
    indicator.config_labels(left_text="Towards head", right_text="Towards foot", fontsize=20)
    indicator.pack()

    indicator2 = tk_indicator(root, 300,100, 10)
    indicator2.set_error_margin(0.1)
    indicator2.set_UI_sensitivity(50)
    indicator2.config_labels(left_text="Too soft", right_text="Too hard", fontsize=20)
    indicator2.pack()
    
    root.mainloop()