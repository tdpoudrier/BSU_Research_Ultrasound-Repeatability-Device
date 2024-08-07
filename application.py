"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: Application to control ultrasound scans to allow for repeatability
"""
#Import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from Custom_tk_widgets.canvas_indicator import tk_indicator
from Custom_tk_widgets.Searchbox import Searchbox

#Import sensors
from peripherals.as5600 import as5600
from peripherals.openscale import openscale
from peripherals.button import button

#Import file processors
from patient_filewriter import patient_filewriter
import csv_processor

from patient import patient


"""
Global patient information
"""
current_patient: patient = None
main_patients_list = None
patients_string_list = None


"""
Scanning globals
"""
image_count = 0
first_scan_start_pos = 0
repeat_scan_expected = []
timerID = None

def testSelected():
    '''
    Display patient selection UI depending on type of test selected
    '''
    choice = selected_scan.get()

    #New scan
    if(choice == 0):
        #hide repeat scan frames, show first scan frames
        new_patient_frame.grid(column=0,row=1)
        return_patient_frame.grid_forget()
        force_indicator_bar.grid_forget()
        force_label.grid_forget()
        
        #clear and enable position entries
        for widget in patient_position_frame.winfo_children():
                if(type(widget) == Entry):
                    widget.config(state="normal")
                    widget.delete(0,"end")
    #Repeat scan
    else:
        patient_searchbox.set_values(patients_string_list) #update searchbox list
        
        #hide first scan and show repeat scan frames
        return_patient_frame.grid(column=0,row=1)
        new_patient_frame.grid_forget()
        force_indicator_bar.grid(column=1, row=2)
        force_label.grid(column=0, row=2)
        
        #clear and disable position entries
        for widget in patient_position_frame.winfo_children():
                if(type(widget) == Entry):
                    widget.delete(0,"end")
                    widget.config(state="readonly")
        

def start_scan():
    '''
    Event for start_btn
    Starts the selected test and updates UI
    asks for confirmation
    '''

    #confirmation
    confirmed = False
    choice = selected_scan.get()
    
    #First scan
    if (choice == 0):
        #Check all information is enterd
        if (patient_study.get() == "" or patient_id.get() == ""):
            messagebox.showerror("Error", "Missing patient information")
            return
        
        #Check all position data is entered
        for widget in patient_position_frame.winfo_children():
            if(type(widget) == Entry):
                if(widget.get() == ""):
                    messagebox.showerror("Error", "Missing patient information")
                    return
        
        #Check that interval is a valid number
        try:
            float(interval_entry.get())
        except:
            messagebox.showerror("Error", "Invalid interval")
            return
        
        #Confirm information
        confirmed = messagebox.askyesno("Confirmation", "You entered: %s, %s\nLeg: %s\nscanner: %s\nfoot: %s\nangle: %s\nIs this correct?" % (patient_study.get(), patient_id.get(), leg_entry.get(), scan_entry.get(), foot_entry.get(), angle_entry.get()))
    
    #Repeat scan
    else:
        #Check patient is selected
        if (patient_searchbox.get_entry_text() == ""):
            messagebox.showerror("Error", "Please select a patient")
            return
        
        #Confirm information
        confirmed = messagebox.askyesno("Confirmation", "You selected:\n\t%s\nIs this correct?" % (patient_searchbox.get_entry_text()))
    
    #User selects no on confirmation message box, prevent scan from starting
    if(confirmed != True):
        return

    #start scan based on type    
    if (selected_scan.get() == 0):
        start_new_scan()
    else:
        start_repeat_scan()
    
    #Update ui into scanning mode
    first_scan_select.config(state="disabled")
    repeat_scan_select.config(state="disabled")
    start_btn.config(state='disabled')
    undo_btn.config(state="normal")
    stop_btn.config(state='normal')

def start_new_scan():
    '''
    Start a scan with a new patient
    '''
    global current_patient
    global first_scan_start_pos

    #Update status indicator
    status_indicator.config(bg='light blue')
    status_indicator.itemconfig(status_text, text="First Scan in progress")

    messagebox.showinfo("Start Position", "Move scanner to starting position")
    first_scan_start_pos = encoder.get_position()
    image_counter_label.config(text="Image count: %d" % (image_count))

    #Initialize current patient, add to list
    current_patient = patient(patient_study_entry.get(), patient_id_entry.get(), leg_entry.get(), scan_entry.get(), foot_entry.get(), angle_entry.get())
    current_patient = patient_file_helper.add_patient(current_patient)
    patient_file_helper.create_patient_file(current_patient)

    #disable patient data widgets
    patient_study_entry.config(state="disabled")
    patient_id_entry.config(state="disabled")
    interval_entry.config(state="disabled")
    
    #disable all position data widgets
    for widget in patient_position_frame.winfo_children():
            if(type(widget) == Entry):
                widget.config(state="disabled")

    first_scan_timer()

def first_scan_timer():
    """
    Display the position error for the first scan
    """
    global timerID, image_count, first_scan_start_pos
    #get data
    current_position = encoder.get_position()
    target_position = first_scan_start_pos - float(interval_entry.get()) * image_count

    #Update UI
    position_indicator_bar.update(current_position, target_position)

    #loop timer
    timerID = root.after(50, first_scan_timer)

def record_scan_data():
    """
    Save current sensor data to patient data file
    """
    global current_patient

    #Format data
    str_speed = "{:.2f}".format(encoder.get_position())
    str_force = "{:.2f}".format(load_cell.get_force())

    #Save data
    patient_file_helper.save_patient_scan_data(current_patient, [str_speed,str_force])

def start_repeat_scan():
    """
    Get the patient scan data and save to global, start reading data
    """
    #Get data from file
    global current_patient, repeat_scan_expected, timerID

    repeat_scan_expected = patient_file_helper.get_patient_scan_data(current_patient)
    
    patient_searchbox.disable()
    image_counter_label.config(text="Image count: 0/%d" % len(repeat_scan_expected))

    #update status indicator
    status_indicator.config(bg='orange')
    status_indicator.itemconfig(status_text, text="Repeat Scan in progress")

    #start displaying error and waiting for user to press button
    timerID = root.after(1, repeat_scan_timer)
        

def repeat_scan_timer():
    """
    Read the current target and display error for each sensor. image_count is incremented when GPIO button is pressed
    """
    global image_count, repeat_scan_expected, timerID

    #end test once all scan data is complete
    if (image_count+1 > len(repeat_scan_expected)):
        stop_scan()
        return

    #get data
    current_force = load_cell.get_force()
    current_speed = encoder.get_position()
    target_force = float(repeat_scan_expected[image_count][1])
    target_speed = float(repeat_scan_expected[image_count][0])

    #Update UI
    force_indicator_bar.update(current_force, target_force)
    position_indicator_bar.update(current_speed, target_speed)

    #loop timer
    timerID = root.after(50, repeat_scan_timer)

def request_stop_scan():
    """
    Open messagebox asking yes or not to stop the current scan
    """
    confirm_stop = messagebox.askyesno("Confirm stop", "Stop the current scan?")
    if (confirm_stop == False):
        return
    stop_scan()

def stop_scan():
    """
    Stop the scan
    """
    global timerID, image_count, current_patient, patients_string_list, main_patients_list

    if timerID is not None:

        #stop displaying sensor error
        root.after_cancel(timerID)
        timerID = None

        #Update scan control buttons
        start_btn.config(state='normal')
        undo_btn.config(state="disabled")
        stop_btn.config(state='disabled')

        #stop first scan
        if selected_scan.get() == 0:
            #Enable data entry widgets
            patient_study_entry.config(state="normal")
            patient_id_entry.config(state="normal")
            interval_entry.config(state="normal")

            #enable position widgets
            for widget in patient_position_frame.winfo_children():
                if(type(widget) == Entry):
                    widget.config(state="normal")

            #Reset patient
            current_patient = None
            
            messagebox.showinfo("", "Scan complete")

            #Get updated patient list
            main_patients_list = patient_file_helper.get_patients()
            patients_string_list = patient_file_helper.get_patients_ui()
        
        #stop repeat scan
        else:
            #Enable patient selection
            patient_searchbox.enable()
            patient_searchbox.set_values(patients_string_list) #update searchbox list
            
            #Display messagebox based on how scan was terminated
            if (image_count+1 > len(repeat_scan_expected)):
                messagebox.showinfo("", "Scan Complete")
            else:
                messagebox.showinfo("", "Scan Stopped")

        #Clear scan data
        image_count = 0
        repeat_scan_expected.clear()
    
        #Enable scan select radio buttons
        first_scan_select.config(state="normal")
        repeat_scan_select.config(state="normal")

        #Reset status indicator
        status_indicator.config(bg='yellow')
        status_indicator.itemconfig(status_text, text="Idle")

def save_image():
    """
    Save or increment data for scans. Called by GPIO button
    """
    global image_count, timerID

    if (timerID == None):
        print("invalid press, returned")
        return

    image_count += 1

    #First scan
    if(selected_scan.get() == 0):
        record_scan_data()
        image_counter_label.config(text="Image count: %d" % (image_count))
    #Repeat scan
    else:
        image_counter_label.config(text="Image count: %d/%d" % (image_count, len(repeat_scan_expected)))

def update_pos(event):
    """
    Update the position entries when the selected patient in the searchbox changes
    """
    global current_patient

    #Get selected patient
    index = patient_searchbox.get_selected_index()
    if (index != None):
        current_patient = main_patients_list[index]
        patient_data = current_patient.get_data()

        #update all position widgets with the correlated patient information
        i = 2
        for widget in patient_position_frame.winfo_children():
                if(type(widget) == Entry):
                    widget.config(state='normal')
                    widget.delete(0,'end')
                    widget.insert(0, patient_data[i])
                    widget.config(state='readonly')
                    i += 1
    #No patient selected
    else:
        current_patient = None
        
        for widget in patient_position_frame.winfo_children():
                if(type(widget) == Entry):
                    widget.delete(0,"end")

def undo_image():
    """
    Remove the previously saved image
    """
    global image_count
    
    #Check there is an image to remove
    if(image_count <= 0):
        messagebox.showerror("Undo Image", "No images to remove")
        return
    
    #Delete previous image
    patient_file_helper.remove_patient_scan_data(current_patient, image_count)
    image_count -= 1

    #Update image count label
    #First scan
    if(selected_scan.get() == 0):
        image_counter_label.config(text="Image count: %d" % (image_count))
    #Repeat scan
    else:
        image_counter_label.config(text="Image count: %d/%d" % (image_count, len(repeat_scan_expected)))



def on_closing():
    """
    Close peripherals before destroying application 
    """
    encoder.close()
    load_cell.close()
    save_button.close()
    root.destroy()

if __name__ == "__main__":    
    messagebox.showinfo("Reset Position", "Please move scanner to the bottom of rail then press ok")
    
    #Config file
    new_config = csv_processor.create_csv_if_missing("./config.csv")
    if(new_config):
        default_config = [
            ["position_error_margin", 0.3],
            ["position_display_sensitivity", 50],
            ["force_error_margin", 0.1],
            ["force_display_sensitivity", 30]
            ["encoder_calibration", -1.8122e-05]
        ]
        for config in default_config:
            csv_processor.append_csv("./config.csv", config)

    #Create sensors
    encoder = as5600()
    encoder.linear_calibration_factor = float(csv_processor.get_line(5, "./config.csv")[1]) * -1
    load_cell = openscale()
    save_button = button(pin=7)
    save_button.set_callbacks(falling=save_image)

    #Get patients list
    patient_file_helper = patient_filewriter("./patients.csv", "./patient_scan_data/")
    main_patients_list = patient_file_helper.get_patients()
    patients_string_list = patient_file_helper.get_patients_ui()

    #Initialize Tkinter
    root = Tk()
    root.title("Ultrasound Repeatability Software")
    root.resizable(width=False,height=False)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=18)

    '''
    Define frames for organizing interface
    '''
    selection_frame = ttk.Frame(root, padding=10)   #contains test and patient selection widgets
    scanning_frame = ttk.Frame(root, padding=10)    #contains active scanning widgets
    select_scan_frame = ttk.Frame(selection_frame, padding=10)  # radio buttons for scan selection
    new_patient_frame = ttk.Frame(selection_frame, padding=10, relief="sunken") # new patient entry widgets
    return_patient_frame = ttk.Frame(selection_frame, padding=10, relief='sunken')  # returing patient selection widgets
    indicator_frame = ttk.Frame(scanning_frame, relief='sunken', padding=10)    # display sensor error widgets
    scan_control_frame = ttk.Frame(scanning_frame, padding=10, relief='raised') # buttons to control scanning
    patient_position_frame = ttk.Frame(selection_frame, relief='sunken', padding=10)

    '''
    Widget Definitions
    '''
    #selection_frame
    selected_scan=IntVar(value=0)
    first_scan_select = Radiobutton(select_scan_frame, text="First Scan", 
                                    value=0, variable=selected_scan, command=testSelected,
                                    background="light grey", selectcolor="light blue", indicator=0,
                                    height=2, width = 10)
    repeat_scan_select = Radiobutton(select_scan_frame, text="Repeat Scan", 
                                     value=1, variable=selected_scan, command=testSelected,
                                     background="light grey", selectcolor="light blue", indicator=0,
                                     height=2, width = 10)

    #new_patient_frame
    patient_study = StringVar()
    patient_id = StringVar()
    patient_study_entry = ttk.Entry(new_patient_frame, textvariable=patient_study)
    patient_id_entry = ttk.Entry(new_patient_frame, textvariable=patient_id)
    study_label = ttk.Label(new_patient_frame, text="Study:")
    id_label = ttk.Label(new_patient_frame, text="ID:")
    interval_label = Label(new_patient_frame, text="Distance between images (m)", wraplength=150, justify="center", font=("Arial",10))
    interval_entry = Entry(new_patient_frame, width=8)

    #return_patient_frame
    select_patient_label = ttk.Label(return_patient_frame, text="Select Patient")
    patient_searchbox = Searchbox(return_patient_frame, values=patients_string_list, width=20)
    patient_searchbox.Listbox.config(font=("Arial", 10), height=4)
    patient_searchbox.bind("<<SearchboxSelect>>", update_pos)
    patient_listbox = Listbox(return_patient_frame)


    #patient_position_frame
    leg_label = ttk.Label(patient_position_frame, text="Leg")
    scan_label = ttk.Label(patient_position_frame, text="Scanner")
    foot_label = ttk.Label(patient_position_frame, text="Foot")
    angle_label = ttk.Label(patient_position_frame, text="Angle")
    leg_entry = Entry(patient_position_frame, readonlybackground="gray90", width=10)
    scan_entry = Entry(patient_position_frame, readonlybackground="gray90", width=10)
    foot_entry = Entry(patient_position_frame, readonlybackground="gray90", width=10)
    angle_entry = Entry(patient_position_frame, readonlybackground="gray90", width=10)

    
    #indicator_frame
    image_counter_label = Label(indicator_frame, text="Image count: 0")
    force_label = ttk.Label(indicator_frame, text="Force:")
    position_label = ttk.Label(indicator_frame, text="Position:")
    
        #force indicator, get parameters from config file
    force_indicator_bar = tk_indicator(indicator_frame,200,50,5)
    force_indicator_bar.config_labels("Too Soft", "Too Hard", 10)
    force_indicator_bar.set_error_margin(float(csv_processor.get_line(3, "./config.csv")[1]))
    force_indicator_bar.set_UI_sensitivity(float(csv_processor.get_line(4, "./config.csv")[1]))

        #postion indicator, get parameters from config file
    position_indicator_bar = tk_indicator(indicator_frame,200,50,5)
    position_indicator_bar.config_labels("<-Head", "Foot->", 10)
    position_indicator_bar.set_error_margin(float(csv_processor.get_line(1, "./config.csv")[1]))
    position_indicator_bar.set_UI_sensitivity(float(csv_processor.get_line(2, "./config.csv")[1]))

    #scan_control_frame
    start_btn = ttk.Button(scan_control_frame, text='Start scan', command=start_scan)
    stop_btn = ttk.Button(scan_control_frame, text="Stop scan", state="disabled", command=request_stop_scan)
    undo_btn = Button(scan_control_frame, text="Undo Image", state="disabled", command=undo_image)
    
    
    """
    Placing elements on display
    """
    #configure root columns
    root.grid_columnconfigure(0,weight=1)
    root.grid_columnconfigure(1,weight=1)
    root.grid_columnconfigure(2,weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)

    #selection_frame
    first_scan_select.grid(column=0,row=0, sticky="nsew")
    repeat_scan_select.grid(column=1,row=0, sticky="nsew")

    #return_pation_frame
    select_patient_label.grid(sticky='w')
    patient_searchbox.grid()

    #new_patient_frame
    patient_study_entry.grid(column=1,row=0)
    study_label.grid(column=0,row=0)
    patient_id_entry.grid(column=1, row=1, sticky="NSEW")
    id_label.grid(column=0,row=1)
    interval_label.grid(column=0,row=2)
    interval_entry.grid(column=1,row=2)

    #position_frame
    leg_label.grid(column=0, row=0)
    leg_entry.grid(column=1, row=0)
    scan_label.grid(column=0, row=1)
    scan_entry.grid(column=1, row=1)
    foot_label.grid(column=0, row=2)
    foot_entry.grid(column=1, row=2)
    angle_label.grid(column=0, row=3)
    angle_entry.grid(column=1, row=3)

    #select_scan_frame
    select_scan_frame.grid(sticky='w')
    new_patient_frame.grid(column=0, row=1, sticky="NSEW")
    return_patient_frame.grid(column=0, row=1)
    patient_position_frame.grid(column=2, row=1)

    #scanning_frame
    scan_control_frame.grid(column=0, row=3, padx=20)
    indicator_frame.grid(column=1, row=3)

    #indicator frame
    image_counter_label.grid(column=0,row=0, columnspan=2)
    position_label.grid(column=0, row=1)
    position_indicator_bar.grid(column=1, row=1)
    force_label.grid(column=0, row=2)
    force_indicator_bar.grid(column=1, row=2)

    #scan_control_frame
    start_btn.grid(column=0,row=0, pady=10)
    stop_btn.grid(column=0,row=2, pady=10)
    undo_btn.grid(column=0,row=1, pady=10)
    
    #root layout
    selection_frame.grid(sticky='nsew')
    scanning_frame.grid()

    """
    Define and place status indicator
    """
    status_indicator = Canvas(root,width=400,height=50, bg='yellow')
    status_text = status_indicator.create_text(200,25, text="Idle")
    status_indicator.grid()

    testSelected()
    root.mainloop()