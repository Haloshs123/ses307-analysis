import pandas_implimentation as pi
import pandas as pd

config_path = r'C:\Users\Halos\PycharmProjects\newpython_test\config.txt'
config = pi.read_config_file(config_path)

if __name__ == '__main__':
    # File reading into initial_dataset
    print(f'Using config options: {config}')
    datapath = config["data_file"]
    if str(config['recover_temp_mode']) == "True":
        datapath = config["working_file"]
        print(f"TEMP DATA RECOVERY. LOADED DATA FROM {datapath} INSTEAD OF CONFIG DEFAULT.")
        # Generate working file from the initial dataset (all changes to data should occur in this file only)
    initial_dataset = pd.read_csv(datapath, index_col=0)
    initial_dataset.to_csv(config['working_file'])
    if "Time Stamp [ms]" not in initial_dataset.index.names:
        pi.add_timestamps()

    sigma = 7
    threshold = 0.05 # TODO: Plot how many events are detected based on the threshold chosen

    # THE ACTUAL PIPELINE:
    pi.trim_front_data(500)
    pi.filter_data(sigma=sigma)
    pi.generate_magnitudes()
    pi.detect_events(threshold=threshold)
    pi.print_headers()
    # TODO: From Butler: Perform Fourier transform to determine period (Rotational) component of data and remove it (requires finding the mean of the magnitude data)
    pi.plot_col_data("Acceleration Magnitude (m/s^2)",f"Acceleration_s={sigma}_t={int(threshold*1000)}")
    pi.plot_col_data("Event?",f"Event_detection_s={sigma}_t={int(threshold*1000)}")
    pi.plot_col_data("Velocity Magnitude (m/s)",f"Velocity_s={sigma}_t={int(threshold*1000)}")
    pi.plot_col_data("Displacement Position Magnitude (m)",f"Displacement_s={sigma}_t={int(threshold*1000)}")



