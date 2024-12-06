Data analysis scripting for SES307 accelerometer data. 


main.py contains the current pipeline used for analysis.

pandas implimentation.py contains the functions and (when ran) a framework for testing a pipeline process.

When running, you should update config.txt with appropriate paths and config.txt's reference in both scripts.


/Test Data contains the raw data from each of the example tests and the two actual drops that were performed.

/Working Data contains the temporary data files used and updated during analysis. Setting config recovery_mode to True will cause the scripts to use the temporary data file instead of the raw data file--mainly useful to continue/recover data if a script exits during runtime.

/Outout Data contains data files that are saved during analysis. By default, the pipeline does not save it's analysis data, so this is usually for comparing data output while testing pipelines with "pandas implimentation.py"
