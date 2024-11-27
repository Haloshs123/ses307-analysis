import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg') # defines backend for how figures are to be saved (agg will save as png)
import numpy as np
import pandas as pd

def read_config_file(config_path=r'C:\Users\Halos\PycharmProjects\newpython_test\config.txt'):
    '''reads config file at config_path, and reads each setting & value pair into an array.
    Format of config file should be [setting]: [value].'''
    config_file = open(config_path,mode='r')
    config_options = {}
    for line in config_file:
        for i in range(len(line)):
            if line[i] == ":":
                if len(line) < i+1: raise ValueError(f"Config file: No value found for \"{line}\".")
                config_options[line[:i].strip()] = line[i+1:].strip()
                break
    config_file.close()
    print(f'Config file read with values: ')
    for key in config_options.keys():
        print(f'{key}: {config_options[key]}')
    print()
    return config_options
read_config_file.args = []

# read config file here since it's necessary for many functions
config = read_config_file()

class DataFile():
    '''contains references to its associated file as self.filename and self.path
    contains methods for reading the header and the data'''

    def __init__(self,filename,path='C:\\Users\\Halos\\PycharmProjects\\ses307_data_analysis_tool\\Test Data\\'):
        self.filename = filename
        self.path = path

    def read_header(self):
        '''returns the headers of this objects associated file'''
        with open(os.path.join(self.path,self.filename)) as datafile:
            header = datafile.readline()
        return header

    def read_data(self,lines=None): # accepts lines as a tuple containing the integer range of rows to include. Default all (besides header)
        '''reads this object's file for csv data and returns a 2-n list containing it.'''
        datafile = open(self.path+self.filename)
        datalines = []
        for line in datafile:
            line = line.strip()
            linedata = line.split(',')
            datalines.append(linedata)
        datafile.close()
        if lines != None: dataarray = datalines[lines[0]:lines[1]]
        else: dataarray = datalines[1:]
        return dataarray

def print_menu():
    '''prints out the menu_choices dictionary, which contains each string-function pairing'''
    print("\nAvailable Functions:")
    for key in menu_choices:
        print(f'{key}: {menu_choices[key].__name__}')
print_menu.args = []

def print_datasets():
    '''prints all of the datasets that are currently loaded'''
    print("\nCurrently loaded datasets:")
    for key in dataobjects:
        print(key)
print_datasets.args = []

def quit_func():
    quit()
quit_func.args = []

def select_data(datafile):
    header = datafile.read_header()
    data = datafile.read_data()

    # automatically determines which index contains timestamps
    t_index = None
    for i in range(len(header)):
        colname = header[i]
        if 'time' in colname or 'Time' in colname:
            if t_index != None: raise(f"Multiple columns headed \'time\' or \'Time\' in {datafile}")
            else: t_index = i
    if t_index == None: raise(f'No columns headed for \'time\' or \'Time\' found in {datafile}')
    print(f"Determined index {t_index} contains timestamps")

    # Read timestamps to return variable
    timestamps = []
    for col in data:
        timestamps.append(col[t_index])

    # Query the desired plotted variable
    print(f"Header for {datafile}:")
    print(header)
    print()
    plot_col = str(input("Input the variable column (Index or name) to be plotted:\n"))
    if type(plot_col) == int:
        None
        #TODO resume here. Should select the column and return it as the plotted variable
        #TODO look at PANDAS dataframes--seems to be doing a lot of the work you have here
    plotted = None

    return timestamps, plotted

def plot_data(datafile,plt_config=config['plt_config'],im_dir=config['images_path'],plot_name=None):
    print(f"Plot_data:")
    if plot_name == None:
        im_num = len(os.listdir(im_dir)) + 1
        im_path = os.path.join(im_dir, f"plot{im_num}")
        print(f'No name given. Assigned image path: {im_path}')
    else:
        im_path = os.path.join(im_dir,plot_name)
        print(f'Image path: {im_path}')
    dataset = dataobjects[datafile][:]
    timeset = []
    for datapoint in dataset:
        timeset.append(dataset[-1])
    print(f'Number of time points read: {len(timeset)}')

    timeset,dataset = select_data(datafile)



    print(f'DEBUG: DATASET IS: {dataset}')

    plt.plot(dataset)
    print(f'Dataset {datafile} plotted.')
    plt.savefig(im_path)
    print(f"Image saved to {im_path}")
plot_data.args = ['datafile','plt_config','im_dir','plot_name']

menu_choices = {
    'pm': print_menu,
    'pd': print_datasets,
    'q': quit_func,
    'plot': plot_data
}

def execute_menu_option(choice):
    func = menu_choices[choice]
    if len(func.args) > 0:
        print(f'\nArguments required for {func.__name__}:')
        for arg in func.args:
            print(arg,end=', ')
        print()
    argvals = {}
    for arg in func.args:
        val = input(f'\nEnter value for {arg}:\n')
        if val != '': argvals[arg] = val
    print(f'DEBUG: argvals: {argvals}')
    func(**argvals)

if __name__ == '__main__':
    # dataobjects loads the contents of each datafile and assigns the filename as the key
    dataobjects = {}
    for file in os.listdir(config['data_file']):
        newdata = DataFile(file)
        dataobjects[file] = newdata.read_data()
    print(f'Loaded data files:')
    for key in dataobjects:
        print(key,end=', ')
    print()

    print_menu()
    while True:
        choice = str(input('\nChoose an option: \n'))
        if choice in menu_choices.keys():
            execute_menu_option(choice)
        else: print(f"\n{choice} not a valid function. Use 'pm' to print the menu of available choices.")
