import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg') # defines backend so figures are saved as a png
import numpy as np
import pandas as pd
import os
import vpython as vp
import scipy as sp


def read_config_file(path):
    '''reads config file at path, and reads each setting & value pair into a dictionary.
    Format of config file should be [setting]: [value].'''
    with open(path,mode='r') as config_file:
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
config_path = r'C:\Users\Halos\PycharmProjects\newpython_test\config.txt'
config = read_config_file(config_path)

def update_file(dataset,target_file=config["working_file"]): # updates targeted file with the loaded dataframe
    if type(dataset) != pd.DataFrame:
        raise ValueError("Attempted to update with a non-dataframe dataset")
    print(f'Updating file {target_file} with dataset: {dataset}')
    dataset.to_csv(target_file)
update_file.args = ['dataset',"target_file"]

def add_timestamps():
    t_step = int(config["time_step"])
    print(f"Timestamps not found in {config["working_file"]}. Adding them assuming {t_step} ms between each event.")
    dataset = pd.read_csv(config["working_file"])
    time_list = []
    for i in range(dataset.shape[0]):
        time_list.append(i*t_step)
    time_series = pd.Series(time_list,name="Time Stamp [ms]")
    dataset.insert(len(dataset.columns),"Time Stamp [ms]",time_series)
    update_file(dataset)
add_timestamps.args = []

def print_headers():
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    cols = dataset.columns
    print(f'Columns in dataset:\n {cols}')
print_headers.args = []

def print_times(): # print both the total duration and the time steps (or average time steps)
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    times = dataset.index
    print(f"Time Labels: {times}")
print_times.args = []

def print_raw_data(): # entire dataframe
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    data = dataset
    print(data)
print_raw_data.args = []

def plot_col_data(column_label=None,plot_name=None,ax1_label=None,ax2_label=None,graph_options=config['plt_config']):
    # Input prompt is inside the function so it prints available columns before the reader is prompted
    # TODO: (perhaps in a separate function) automatically determine labels for units/title
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    while not column_label:
        print(f'Available columns:')
        print(dataset.columns)
        column_label = str(input("Enter a column label:\n"))
    data = dataset.loc[:,column_label]
    times = dataset.index*0.001
    print("Plotting Data:")
    print(data)
    if plot_name is None:
        im_num = len(os.listdir(config['images_path'])) + 1
        im_path = os.path.join(config['images_path'], f"plot{im_num}")
        print(f'Assigned image path: {im_path}')
    else:
        im_path = os.path.join(config['images_path'],plot_name)
        print(f'Image path: {im_path}')
    plt.plot(times,data,graph_options)
    plt.xlabel(ax1_label)
    plt.ylabel(ax2_label)
    plt.title(plot_name)
    plt.savefig(im_path)
    plt.close()
    print(f'Plot successfully saved to {im_path}')
plot_col_data.args = ["plot_name"]

def integrate_col(new_column_label,column_label=None): # integrates column using numerical methods
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    if not column_label:
        print(f'Available columns:')
        print(dataset.columns)
        column_label = str(input("Enter a column label:\n"))
    data = dataset.loc[:,column_label].to_numpy()
    print(f'Data column {column_label}:\n{data}')
    times = dataset.index.to_numpy()*0.001
    print(f'Time column:\n{times}')
    integral_result = np.cumsum(data*0.150) # TODO Fix whatever is going wrong here... else something up with data?
    print(f'Integration Result for {new_column_label}:\n{integral_result}')
    print(f"number of dataset columns: {len(dataset.columns)}")
    dataset.insert(len(dataset.columns),new_column_label,integral_result)
    update_file(dataset)
integrate_col.args = ['new_column_label']

def filter_data(sigma=1):
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    filtered_columns = ["Acceleration X (m/s^2)","Acceleration Y (m/s^2)","Acceleration Z (m/s^2)"]
    for column in filtered_columns:
        new_col = sp.ndimage.gaussian_filter(dataset[column],sigma)
        new_col_name = column
        dataset[new_col_name] = new_col
    print(f'Filtered Columns: {filtered_columns}')
    update_file(dataset)
filter_data.args = []

def subtract_median(column_label=None):
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    while not column_label:
        print(f'Available columns:')
        print(dataset.columns)
        column_label = str(input("Enter a column label:\n"))
    median = dataset[column_label].median()
    print(f'Median of {column_label} is {median}. Subtracting...')
    dataset[column_label] = dataset[column_label]-median
    update_file(dataset)
subtract_median.args = []

def integrate_vectors(): # calls integrate_col to acquire velocity and position data
    integrate_col('Velocity X (m/s)', column_label='Acceleration X (m/s^2)')
    integrate_col('Velocity Y (m/s)', column_label='Acceleration Y (m/s^2)')
    integrate_col('Velocity Z (m/s)', column_label='Acceleration Z (m/s^2)')
    integrate_col('Displacement Position X (m)', column_label='Velocity X (m/s)')
    integrate_col('Displacement Position Y (m)', column_label='Velocity Y (m/s)')
    integrate_col('Displacement Position Z (m)', column_label='Velocity Z (m/s)')
integrate_vectors.args = []

def plot_vector_path(): # takes in 3 columns and uses them as xyz vector directions for plotting using vpython
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    x_d = dataset['Displacement Position X (m)'].to_numpy()
    y_d = dataset['Displacement Position Y (m)'].to_numpy()
    z_d = dataset['Displacement Position Z (m)'].to_numpy()
    x_v = dataset['Velocity X (m/s)'].to_numpy()
    y_v = dataset['Velocity Y (m/s)'].to_numpy()
    z_v = dataset['Velocity Z (m/s)'].to_numpy()
    x_a = dataset['Acceleration X (m/s^2)'].to_numpy()
    y_a = dataset['Acceleration Y (m/s^2)'].to_numpy()
    z_a = dataset['Acceleration Z (m/s^2)'].to_numpy()
    times = dataset.index.to_numpy()
    for i in range(len(times)):
        position = vp.vec(x_d[i],y_d[i],z_d[i])
        print(f"DEBUG: Sphere created at position {position}")
        vp.sphere(pos=position,radius=2)

    input("Press [Enter] to continue")
plot_vector_path.args = []

def magnitude(x,y,z):
    return np.sqrt(x.to_numpy()**2 + y.to_numpy()**2 + z.to_numpy()**2)

def generate_magnitudes(overwrite=False):
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    if "Acceleration Magnitude (m/s^2)" in dataset.columns and not overwrite:
        print("Acceleration Magnitude data already in dataset. No calculation performed.")
    elif "Acceleration X (m/s^2)" in dataset.columns and "Acceleration Y (m/s^2)" in dataset.columns and "Acceleration Z (m/s^2)" in dataset.columns:
        print("Acceleration data found in dataset.")
        a_mag = magnitude(dataset["Acceleration X (m/s^2)"],dataset["Acceleration Y (m/s^2)"],dataset["Acceleration Z (m/s^2)"])
        print(f"Acceleration magnitude calculated as:\n{a_mag}")
        if "Acceleration Magnitude (m/s^2)" in dataset.columns:
            dataset["Acceleration Magnitude (m/s^2)"] = a_mag
        else:
            dataset.insert(len(dataset.columns), "Acceleration Magnitude (m/s^2)", a_mag)
        update_file(dataset)
    else:
        print("No Acceleration data found in dataset")

    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    subtract_median("Acceleration Magnitude (m/s^2)")
    if "Velocity Magnitude (m/s)" in dataset.columns and not overwrite:
        print("Velocity Magnitude data already in dataset. No calculation performed.")
    elif  "Acceleration Magnitude (m/s^2)" in dataset.columns:
        print("Generating Velocity Magnitude based on Acceleration Magnitude")
        integrate_col("Velocity Magnitude (m/s)","Acceleration Magnitude (m/s^2)")

    #    elif "Velocity X (m/s)" in columns and "Velocity Y (m/s)" in columns and "Velocity Z (m/s)" in columns:
#        print("Velocity data found in dataset.")
#        v_mag = magnitude(dataset["Velocity X (m/s)"],dataset["Velocity Y (m/s)"],dataset["Velocity Z (m/s)"])
#        print(f"Velocity magnitude calculated as:\n{v_mag}")
#        if "Velocity Magnitude (m/s)" in columns:
#            dataset["Velocity Magnitude (m/s)"] = v_mag
#        else:
#            dataset.insert(len(dataset.columns), "Velocity Magnitude (m/s)", v_mag)
#        update_file(dataset)
#        dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    else:
        print("No Velocity data found in dataset")
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    if "Displacement Position Magnitude (m)" in dataset.columns and not overwrite:
        print("Displacement Position Magnitude data already in dataset. No calculation performed.")
    elif  "Velocity Magnitude (m/s)" in dataset.columns:
        print("Generating Displacement Position Magnitude based on Velocity Magnitude")
        integrate_col("Displacement Position Magnitude (m)","Velocity Magnitude (m/s)")
#    elif "Displacement Position X (m)" in columns and "Displacement Position Y (m)" in columns and "Displacement Position Z (m)" in columns:
#        print("Displacement Position data found in dataset.")
#        d_mag = magnitude(dataset["Displacement Position X (m)"],dataset["Displacement Position Y (m)"],dataset["Displacement Position Z (m)"])
#        print(f"Displacement Position magnitude calculated as:\n{d_mag}")
#        if "Displacement Position Magnitude (m)" in columns:
#            dataset["Displacement Position Magnitude (m)"] = d_mag
#        else:
#            dataset.insert(len(dataset.columns), "Displacement Position Magnitude (m)", d_mag)
#        update_file(dataset)
    else:
        print("No Displacement Position data found in dataset")
generate_magnitudes.args = []

def save_working_file(save_as_name):
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    output_path = config['output_path']
    output_file = os.path.join(output_path,save_as_name)
    print(f'Saving working dataset as "{save_as_name}.CSV". Full path:\n{output_file}.CSV')
    dataset.to_csv(output_file)
    print(f'Save successful.')
save_working_file.args = ['save_as_name']

def detect_events(threshold = 5):
    dataset = pd.read_csv(config["working_file"], index_col="Time Stamp [ms]")
    if "Acceleration Magnitude (m/s^2)" not in dataset.columns:
        raise ValueError(f"Acceleration Magnitude not found in dataset. Calculate Magnitudes before calling detect_events().")
    a = dataset["Acceleration Magnitude (m/s^2)"]
    da = a.diff()
    dadt = da/(float(config["time_step"])*0.001)
    eventcatch = dadt > threshold
    dataset.insert(len(dataset.columns), "Event?", eventcatch)
    update_file(dataset)
detect_events.args = ["threshold"]

def trim_front_data(point_count):
    dataset = pd.read_csv(config["working_file"])
    print(f"Trimming to the {point_count} last rows in dataset.")
    print(f'Previous Dataset:\n{dataset}\n')
    dataset = dataset[-int(point_count):]
    print(f"New dataset:\n{dataset}\n")
    update_file(dataset)
trim_front_data.args = ["point_count"]

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
    'pltv':plot_vector_path,
    'mag':generate_magnitudes,
    'save':save_working_file,
    'filt':filter_data,
    'subm': subtract_median,
    'trim':trim_front_data
}

def execute_menu_option(choice):
    func = menu_choices[choice]
    if len(func.args) > 0:
        print(f'\nArguments required for {func.__name__}:')
        for arg in func.args:
            print(arg, end=', ')
        print()
    argvals = {}
    for arg in func.args:
        val = input(f'\nEnter value for {arg}:\n')
        if val != '': argvals[arg] = val
    #print(f'DEBUG: argvals: {argvals}')
    val = func(**argvals)
    if val is not None:
        print(f'DEBUG: val in this execution returned as: {val}, type: {type(val)}')
        return val

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--datapath",help="Path to dataset to be analyzed. Can be raw test data or a working dataset. If none is provided, uses default in config")
    parser.add_argument("--func",help="Function shortname to be executed. If none is provided, will begine a prompt loop until quit with 'q'")
    args = parser.parse_args()
    datapath = args.datapath
    func = args.func

    # Default parameter for the case of no input
    if not datapath: datapath = config["data_file"]
    if str(config['recover_temp_mode']) == "True":
        datapath = config["working_file"]
        print(f"TEMP DATA RECOVERY. LOADED DATA FROM {datapath} INSTEAD OF CONFIG DEFAULT.")
    # Generate working file from the initial dataset (all changes to data should occur in this file only)
    initial_dataset = pd.read_csv(datapath,index_col=0)
    initial_dataset.to_csv(config['working_file'])
    if "Time Stamp [ms]" not in initial_dataset.index.names:
        add_timestamps()

    if not func:
        print_menu()
        while True:
            choice = str(input('\nChoose a function: \n'))
            if choice in menu_choices.keys():
                val = execute_menu_option(choice)
            else:
                print(f"\n{choice} not a valid function. Use 'pm' to print the menu of available choices.")
    else:
        execute_menu_option(func)
        update_file(initial_dataset, config["working_file"])
