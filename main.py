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
    if "Time Stamp [ms]" not in initial_dataset.index.names and "Time Stamp [ms]" not in initial_dataset.columns:
        pi.add_timestamps()

    sigma = 10
    threshold = 0.08
    dropnum = "OCT12F1"  # Todo: update manually for name of drop data
    window_size = 400 # how many entries at the end are actually used

    # THE ACTUAL PIPELINE:
    pi.trim_front_data(window_size)
    pi.filter_data(sigma=sigma)
    pi.generate_magnitudes()
    pi.detect_events(threshold=threshold)
    pi.print_headers()
    # TODO: From Butler: Perform Fourier transform to determine period (Rotational) component of data and remove it (requires finding the mean of the magnitude data)
    # fourier should probably be done on each individual x/y/z axis since magnitude data probably doesnt oscilate in same way (vector mag fairly consistent)
    pi.plot_col_data(
        column_label="Acceleration Magnitude (m/s^2)",
        plot_name=f"Acceleration, Drop {dropnum}, s={sigma}, t={int(threshold*1000)}",
        ax1_label="Timestamp (s)",
        ax2_label="Acceleration Magnitude (m/s^2)")
    pi.plot_col_data(
        column_label="Event?",
        plot_name=f"Event detection, Drop {dropnum}, s={sigma}, t={int(threshold*1000)}",
        ax1_label="Timestamp (s)",
        ax2_label="Event Detected (T/F)")
    pi.plot_col_data(
        column_label="Velocity Magnitude (m/s)",
        plot_name=f"Velocity Change, Drop {dropnum}, s={sigma}, t={int(threshold*1000)}",
        ax1_label="Timestamp (s)",
        ax2_label="Velocity Change (m/s)")
    pi.plot_col_data(
        column_label="Displacement Position Magnitude (m)",
        plot_name=f"Displacement, Drop {dropnum}, s={sigma}, t={int(threshold*1000)}",
        ax1_label="Timestamp (s)",
        ax2_label="Displacement (m/s)")