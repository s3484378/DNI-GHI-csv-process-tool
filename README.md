# DNI GHI solar data processing tool
Command line script to convert DNI/GHI data into a csv file for a given latitude and longitude

## Description
Takes user input for latitude and longitude and creates two CSV files for the DNI and GHI values for that location for the nearest coordinate found.

For this script to function the following folder/file structure must be present:
```bash
├── DNI-YYYY
│   ├── solar_dni_YYYYMMDD_HHUT.txt
│   ├── ...
├── GHI-YYYY
│   ├── solar_ghi_YYYYMMDD_HHUT.txt
│   ├── ...
├── dni_ghi_script.py
```

YYYY is the year with century representaiton, eg 2013\
MM is the zero-padded month value, eg 01 for January\
DD is the zero-padded day of the month, eg 01 for the 1st\
HH is the zero-padded hour (24 hour clock) of the day, eg 00, 13 for 12:00AM, 01:00PM\
UT represents universal time, this script attempt to find the local timezone for the given\
latitude and longitude to convert the UTC time to local time\
dni_ghi_script.py is the main python script

## Example Usage/Output
From a command line:
### Run the python file directly (tested in Python 3.7) and follow the prompts
```sh
python dni_ghi_script.py
```

### For the user input -37.000, 144.000 and year 2013 the following two files will be generated
```sh
-37.0,144.0_dni.csv
-37.0,144.0_ghi.csv
```

### Additional Info
This script implements multiprocessing as scraping through each file is relatively resource intensive on both the CPU and HDD. With a relatively new quad core i7, the script processes roughly 60 files per second and completes in less than 5 minutes. Note 1 year of DNI and GHI Australia data is roughly 35GB.

## Python Dependencies 3.7.4
```bash
pip install pytz tqdm timezonefinder
```
