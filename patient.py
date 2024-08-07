"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: patient object for ultrasound repeatability application
"""

class patient():
    """
    Stores data related to patient as one object
    """

    def __init__(self, study, id, leg_position, scan_position, foot_pos, angle_pos):
        """
        Initalize the patient
        """
        self.study = study
        self.id = id
        self.leg_positon = leg_position
        self.scan_position = scan_position
        self.foot_pos = foot_pos
        self.angle_pos = angle_pos
        self.iteration = 1
        self.filename = ""
        
    def set_iteration(self, iteration):
        """
        Set the iteration of the patient. Allows for multiple copies of 1 patient to be saved
        """
        self.iteration = ("%03d" % (iteration) )
    
    def get_compare_data(self) -> list:
        """
        Defines how patients are compared, iteration and postion are ignored
        """
        return [self.study, self.id]
    
    def to_string(self):
        """
        Get simplified string representation
        """
        return self.study + "_" + self.id + "_" +  self.iteration

    def get_data(self) -> list:
        """
        Get all patient data as a list
        """
        return [self.study, self.id, self.leg_positon, self.scan_position, self.foot_pos, self.angle_pos, self.iteration]
    
    def generate_filename(self, directory):
        """
        Generate the filename for the patient based on the given directory
        """
        self.filename = directory + "/" + self.study + "_" + self.id + "_" + self.iteration + ".csv"