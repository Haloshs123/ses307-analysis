import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg') # defines backend so figures are saved as a png
import pandas as pd
import os
import scipy as sp

''' 
Valid functions:   
    'pm': print_menu,
    'q': quit_func,
    'up': update_file,
    'ph': print_headers,
    'pt': print_times,
    'pr': print_raw_data,
    'plot':plot_col_data,
    'int': integrate_vectors,
    'pltv':plot_vector_path'''

def read_config_file(config_path=r'C:\Users\Halos\PycharmProjects\newpython_test\config.txt'):
    '''reads config file at config_path, and reads each setting & value pair into an array.
    Format of config file should be [setting]: [value].'''
    with open(config_path,mode='r') as config_file:
        config_options = {}
        for line in config_file:
            for i in range(len(line)):
                if line[i] == ":":
                    if len(line) < i+1: raise ValueError(f"Config file: No value found for \"{line}\".")
                    config_options[line[:i].strip()] = line[i+1:].strip()
                    break
    print(f'Config file read with values: ')
    for key in config_options.keys():
        print(f'{key}: {config_options[key]}')
    print()
    return config_options
read_config_file.args = []
# read config file here (not main) since it's settings are necessary for many functions
config = read_config_file()

def update_file(dataset,target_file = r"C:\Users\Halos\PycharmProjects\newpython_test\Working Data\temp"): # updates targeted file with the loaded dataframe
    # todo: implement a prompt to avoid overwriting a working file
    dataset.to_csv(target_file)
    return target_file
update_file.args = ["target_file","dataset"]

def print_headers(dataset):
    cols = dataset.columns
    print(f'Columns in dataset:\n {cols}')
    return cols
print_headers.args = ["dataset"]

def print_times(dataset): # print both the total duration and the time steps (or average time steps)
    times = dataset.index
    print(f"Time Labels: {times}")
    return times
print_times.args = ['dataset']

def print_raw_data(dataset): # entire dataframe
    data = dataset
    print(data)
    return data
print_raw_data.args = ['dataset']

def plot_col_data(dataset,column_label=None,plot_name=None):
    # Input prompt is inside the function so it prints available columns before the reader is prompted
    # TODO: (perhaps in a separate function) automatically determine labels for units/title
    if not column_label:
        print(f'Available columns:')
        print(dataset.columns)
        column_label = str(input("Enter a column label:\n"))
    data = dataset.loc[:,column_label]
    times = dataset.index
    print("Plotting Data:")
    print(data)
    if plot_name == None:
        im_num = len(os.listdir(config['images_path'])) + 1
        im_path = os.path.join(config['images_path'], f"plot{im_num}")
        print(f'Assigned image path: {im_path}')
    else:
        im_path = os.path.join(config['images_path'],plot_name)
        print(f'Image path: {im_path}')
    plt.plot(times,data,config['plt_config'])
    plt.savefig(im_path)
    print(f'Plot successfully saved to {im_path}')
plot_col_data.args = ['dataset',"plot_name"]

def integrate_col(dataset,new_column_label,column_label=None,target_file=None): # integrates column using scipy
    if not column_label:
        print(f'Available columns:')
        print(dataset.columns)
        column_label = str(input("Enter a column label:\n"))
    data = dataset.loc[:,column_label]
    times = dataset.index
    # create list for new column data
    # for i in range len(data): (do check to ensure its also length of times but should be)
    #
    #
    #   dataset.insert(

    # TODO integrate w/rt time scipy
    # append new data column to working data file (if it already exists, prompt for confirmation and pop previous column)
    update_file(dataset,)
integrate_col.args = ['dataset','new_column_label']

def integrate_vectors(dataset): # calls integrate_col to acquire velocity and position data
    integrate_col(dataset, 'Velocity X (m/s)', column_label='Acceleration X (m/s^2)')
    integrate_col(dataset, 'Velocity Y (m/s)', column_label='Acceleration Y (m/s^2)')
    integrate_col(dataset, 'Velocity Z (m/s)', column_label='Acceleration Z (m/s^2)')
    integrate_col(dataset, 'Displacement Position X (m)', column_label='Velocity X (m/s^2)')
    integrate_col(dataset, 'Displacement Position Y (m)', column_label='Velocity Y (m/s^2)')
    integrate_col(dataset, 'Displacement Position Z (m)', column_label='Velocity Z (m/s^2)')
integrate_vectors.args = ['dataset']

def plot_vector_path(dataset): # takes in 3 columns and uses them as xyz vector directions for plotting using vpython
    raise NotImplementedError
# Todo: vpython to visualize vectors during path (should plot velocity+acceleration vectors with tails at position in 3d space)
plot_vector_path.args = ['dataset']

def print_menu():
    '''prints out the menu_choices dictionary, which contains each string-function pairing'''
    print("\nAvailable Functions:")
    for key in menu_choices:
        print(f'{key}: {menu_choices[key].__name__}')
print_menu.args = []

def quit_func():
    quit()
quit_func.args = []

menu_choices = {
    'pm': print_menu,
    'q': quit_func,
    'up': update_file,
    'ph': print_headers,
    'pt': print_times,
    'pr': print_raw_data,
    'plot':plot_col_data,
    'int': integrate_vectors,
    'pltv':plot_vector_path
}

def execute_menu_option(choice,dataset):
    func = menu_choices[choice]
    if len(func.args) > 0:
        print(f'\nArguments required for {func.__name__}:')
        for arg in func.args:
            print(arg, end=', ')
        print()
    argvals = {}
    for arg in func.args:
        if arg == "dataset":
            val = dataset
            argvals[arg] = val
        else:
            val = input(f'\nEnter value for {arg}:\n')
            if val != '': argvals[arg] = val
    #print(f'DEBUG: argvals: {argvals}')
    func(**argvals)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath",help="Path to dataset to be analyzed. Can be raw test data or a working dataset. If none is provided, uses default in config")
    parser.add_argument("--func",help="Function shortname to be executed. If none is provided, will begine a prompt loop until quit with 'q'")
    args = parser.parse_args()
    datapath = args.datapath
    func = args.func

    # Default parameters for the case of no input
    if not datapath:   datapath = config["data_file"]
    dataset = pd.read_csv(datapath,index_col="Time Stamp [ms]")

    if not func:
        print_menu()
        while True:
            choice = str(input('\nChoose a function: \n'))
            if choice in menu_choices.keys():
                execute_menu_option(choice,dataset)
            else:
                print(f"\n{choice} not a valid function. Use 'pm' to print the menu of available choices.")
    else:
        execute_menu_option(func,dataset)



#    TODO:
#    Functionality:
#    - plot single column data to time axis
#    - vector add acceleration columns (append to current file) (find module for vector addition? nvm this is literally probably just numpy)
#    - scipy/numpy integrate acceleration for velocity vector (append to file)
#    - scipy/numpy integrate velocity for position vector (append to file)
#    - "Noise signal removal"
#    - "Event detection" with vibration sensors?




