"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: file writing for the patient object
"""
import csv_processor
from patient import patient

class patient_filewriter():

    def __init__(self, patient_file, data_dir):
        """
        Create patient file and storage directory if needed
        """
        
        self.patients_filename = patient_file
        self.dir_data = data_dir
        
        file_created = csv_processor.create_csv_if_missing(self.patients_filename)
        if file_created == True:
            csv_processor.append_csv(self.patients_filename, ["Study","ID","Leg_Pos","Scanner_Pos","Foot_Pos", "Angle_Pos", "Iteration"])

        csv_processor.create_directory_if_missing(self.dir_data)

    def create_patient_file(self, patient: patient):
        """
        Creates patient data file
        """
        filename = self.dir_data + patient.to_string() + ".csv"
        patient.filename = filename
        open(filename, 'x', newline='')
    
    def add_patient(self, new_patient: patient):
        '''
        add patient to list, check if duplicates exist and increment iteration counter

        '''
        prev_patients = self.get_patients()

        #Remove iteration number to simplify counting iterations
        compare_list = []
        for prev_patient in prev_patients:
            compare_list.append(prev_patient.get_compare_data())
        
        #Add iteration number to patient
        iteration = compare_list.count(new_patient.get_compare_data())
        new_patient.set_iteration(iteration + 1) #start from 1 not 0
        new_patient.generate_filename(self.dir_data)
        
        csv_processor.append_csv(self.patients_filename, new_patient.get_data())

        return new_patient

    def get_patients(self) -> list[patient]:
        '''
        Get list of patients that have been scanned.
        Parses patients stored in txt file to patient objects
        '''  
        lines = csv_processor.get_lines(self.patients_filename)
        
        #Ignore header
        lines = lines[1:]

        lines.sort(key=self.sort)

        #Convert to list of patients
        list = []
        for item in lines:
            a_patient = patient(item[0], item[1], item[2], item[3], item[4], item[5])
            a_patient.set_iteration(int(item[6]))
            a_patient.generate_filename(self.dir_data)
            list.append(a_patient)
        
        return list
    
    def sort(self, list):
        """
        Sort based on study and id
        """
        return list[0].lower() + list[1].lower()
    
    def save_patient_scan_data(self, patient:patient, data):
        """
        Save data to patient file
        """
        csv_processor.append_csv(patient.filename, data)
    
    def remove_patient_scan_data(self, patient:patient, line_index):
        """
        Remove a line of data from the patient's data file
        """
        csv_processor.remove_line(patient.filename, line_index)
    
    def get_patient_scan_data(self, patient:patient) -> list[str]:
        """
        Get all datalines from patient file
        """
        return csv_processor.get_lines(patient.filename)
    
    def get_patients_ui(self) ->list[str]:
        """
        Gets a list of all patients represented as strings, intended for ui displays
        """
        patients = self.get_patients()

        str_list = []
        for patient in patients:
            str_list.append(patient.study + "," + patient.id + "," + patient.iteration)
        
        return str_list
    
if __name__ == "__main__":
    writer = patient_filewriter("./patients.csv", "./patient_scan_data")
    
    prev_patients = writer.get_patients()

    # new_patient = patient("mkr", "102", 4, 5)
    # writer.add_patient(new_patient)

    data = writer.get_patient_scan_data(prev_patients[0])
    print(data)

    print(type(writer.get_patients()[0]))
    print((writer.get_patients_ui()))
    # # print(type(writer.get_patients_ui()[0]))