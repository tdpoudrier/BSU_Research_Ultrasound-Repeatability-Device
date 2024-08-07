"""
    Author: Tevin Poudrier
    Date: Wed Jul 17 12:40:48 AM MDT 2024
    Description: Custom tkinter widget for searching a listbox widget when typing in the entry widget
"""
from tkinter import *

class Searchbox(Frame):
    """
    Custom tkinter widget for searching a listbox widget when typing in the entry widget. Triggers "<<SearchboxSelect>>" when an item is selected.
    """
    
    def __init__(self, parent, values, *args, **kwargs):
        """
        Custom tkinter widget for searching a listbox widget when typing in the entry widget
        """
        Frame.__init__(self,parent, *args, **kwargs)
        
        #Define entry
        self.Entry = Entry(self) 
        self.Entry.bind('<KeyRelease>', self.filter_list)
        self.Entry.bind("<Button-1>", self.__clear_selected__) 
        
        #set the values of the listbox
        self.values = values
        self.Listbox = Listbox(self) 
        self.Listbox.bind('<<ListboxSelect>>', self.__save_selected__)
        self.update(self.values) 

        #attach scrollbar to listbox
        self.scroll = Scrollbar(self, command= self.Listbox.yview)
        self.Listbox['yscrollcommand'] = self.scroll.set

        #layout
        self.Entry.grid(column=0,row=0, sticky='nsew') 
        self.Listbox.grid(column=0,row=1, sticky='nsew')
        self.scroll.grid(column=1, row=1, sticky='ns')


    def filter_list(self, event):
        '''
        Filter the elements in the list to only
        show elements that contain the text entered
        ''' 
        
        #Get text in entry widget
        entry_text = event.widget.get() 
        
        #Set to full list when text is empty
        if entry_text == '': 
            new_list = self.values 
        
        #Filter list
        else: 
            new_list = [] 
            for item in self.values: 
                if entry_text.lower() in item.lower(): 
                    new_list.append(item)                 
    
        self.update(new_list) 
    
    
    def update(self, filtered_data):
        '''
        update data in listbox 
        ''' 

        #Empty list
        self.Listbox.delete(0, 'end') 
    
        #Populate list with filtered elements
        for item in filtered_data: 
            self.Listbox.insert('end', item)
    
    def __clear_selected__(self,event):
        """
        Empty the entry and deselect any items in the listbox
        """
        self.Entry.delete(0, 'end')
        self.Listbox.selection_clear(0, 'end')
    
    def __save_selected__(self, event):
        """
        Update the entry with the selected listbox item, triggers "<<SearchboxSelect>>" event
        """
        selected_list = event.widget.curselection()
        for i in selected_list:
            self.Entry.delete(0, 'end')
            self.Entry.insert(0, self.Listbox.get(i))
        self.event_generate("<<SearchboxSelect>>")


    def set_values (self, new_values=[]):
        '''
        Set the default values of the searchbox
        '''
        self.values = new_values 
        self.update(new_values)
    
    def curselection(self):
        """
        Returns indices of currently selected item in the FILTERED list
        """
        try:
            return self.Listbox.curselection()[0]
        except:
            return None
    
    def get_selected(self):
        """
        Get the selected item
        """
        filtered_index = self.curselection()
        if (filtered_index != None):
            selected_item = self.Listbox.get(filtered_index)
            # print(selected_item)
            return selected_item
        else:
            # print(filtered_index)
            # print(type(filtered_index))
            return None
    
    def get_selected_index(self):
        """
        Returns the index of the selected item in the ENTIRE list
        """
        selected_item = self.get_selected()
        
        if(selected_item != None):
            index = self.values.index(selected_item)
            return index
        else:
            return None
    
    def get_entry_text(self):
        """
        Gets the text in the entry widget
        """
        return self.Entry.get()

    def enable(self):
        """
        Enable editing and selecting of the Searchbox
        """
        self.Entry.config(state="normal")
        self.Listbox.config(state="normal")

    def disable(self):
        """
        Disable editing and selecting of the Searchbox
        """
        self.Entry.config(state="disabled")
        self.Listbox.config(state="disabled")

if __name__ == "__main__":

    def searchbox_select(*args):
        print(searchbox.get_selected_index())

    listy = ('C','C++','Java', 
        'Python','Perl', 
        'PHP','ASP','JS','C++','Java', 
        'Python','Perl', 
        'PHP','ASP','JS','C++','Java', 
        'Python','Perl', 
        'PHP','ASP','JS','C++','Java', 
        'Python','Perl', 
        'PHP','ASP','JS' ) 
    
    root = Tk() 
    
    #creating text box  
    searchbox = Searchbox(root, values=listy)
    searchbox.pack()

    root.bind("<<SearchboxSelect>>", searchbox_select)
    
    root.mainloop() 