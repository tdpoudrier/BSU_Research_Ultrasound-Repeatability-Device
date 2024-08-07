"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: static methods to help with reading and writing data to csv files
"""
import csv
import os

def create_csv_if_missing(file_path) -> bool:
    '''
    Create a new csv if it doesnt already exist. Returns true when file is created, false otherwise.
    file path must end in .csv
    '''
    if (os.path.isfile(file_path) == False):
        open(file_path, 'x', newline='')
        return True
    else:
        return False

def create_directory_if_missing(dir_path) -> bool:
    """
    Create a new directory if it doesnt already exist. Returns true when directory is created, false otherwise
    """
    if (os.path.isdir(dir_path) == False):
        os.mkdir(dir_path)
        return True
    else:
        return False

def append_csv(filename, data:list):
    '''
    Append data to file as a new line
    '''
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_NONE)
        writer.writerow(data)

def get_lines(filename) -> list[list[str]]:
    """
    Get all lines stored in the csv file
    """
    with open(filename, 'r', newline='') as file:
        csv_file = csv.reader(file)

        #get all lines
        list = []
        for line in csv_file:
            list.append(line)

        return list
    
def get_line(index, filename) -> list[str]:
    """
    Get one line of data from filename at the index. Index starts at 1
    """
    lines = get_lines(filename)
    return lines[index-1]

def remove_line(filename, index):
    """
    Remove one line of data from filename at the index. Index starts at 1 
    """
    prev_list = get_lines(filename)
    
    try:
        removed_line = prev_list.pop(index-1)
    except Exception as error:
        print("unable to remove line " + str(index))
        print(error)
        return
    
    #Clear file and add lines back in without the removed line
    clear(filename)
    for line in prev_list:
        append_csv(filename, line)

def clear(filename):
    """
    Clear all data in the file
    """
    open(filename, 'w').close()


if __name__ == "__main__":
    remove_line("./MSK_99_001.csv", 1)