# Ben Soutter 2019
import os, csv, signal, pytz
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from datetime import datetime
from timezonefinder import TimezoneFinder
dir_names = ["dni","ghi"]

# debug levels 0 -> none, 1 -> important, 2 -> all
debug = 0

# Compile the script into .exe that can be run without requiring python
# pyinstaller --onefile .\gui.py

# Global exit
stop_script = False

# Multiprocessing max simultaneous tasks (number of cores on PC)
max_processes = cpu_count()

# def process_file(filename, lat, lon):
def process_file(arg):
    filename = arg[0]
    lat = arg[1]
    lon = arg[2]
    with open(filename) as f:
        try:
            dt = datetime.strptime(os.path.basename(filename).replace("solar_ghi_", '').replace("solar_dni_", '').replace("UT.txt", '').replace('_', ''), "%Y%m%d%H").replace(tzinfo=pytz.timezone('UTC'))
            if debug: print("Timestamp: {}".format(dt))
        except:
            print("Error converting datetime value for {}!".format(filename))
            exit()
        reader = csv.reader(f, delimiter=' ')
        ncols = 0
        nrows = 0
        xll = 0
        yll = 0
        cellsize = 0
        no_data = 0
        row_no = 0
        lat_vals_diff = dict()
        long_vals_diff = dict()
        long_column_index = 0
        for row in reader:
            # read file information
            if(len(row) == 2):
                if row[0].upper() == "NCOLS":
                    ncols = int(row[1])
                    if debug == 2: print("ncols:", ncols)
                elif row[0].upper() == "NROWS":
                    nrows = int(row[1])
                    if debug == 2: print("ncols:", nrows)
                elif row[0].upper() == "XLLCORNER":
                    xll = float(row[1])
                    if debug == 2: print("xll:", xll)
                elif row[0].upper() == "YLLCORNER":
                    yll = float(row[1])
                    if debug == 2: print("yll:", yll)
                elif row[0].upper() == "CELLSIZE":
                    cellsize = float(row[1])
                    if debug == 2: print("cellsize:", cellsize)
                elif row[0].upper() == "NODATA_VALUE":
                    no_data = int(row[1])
                    if debug == 2: print("no_data:", no_data)
            elif len(row) == ncols:
                # Calculate top left coord - first data point
                if(not row_no):
                    yul = yll + ((nrows-1)*cellsize)
                
                    # Find long value
                    for i in range(0, len(row)):
                        
                        # Store long value (difference between target value entered), and respective DNI/GHI value for that row
                        long_vals_diff[abs(lon - (xll + (i * cellsize)))] = [i, (xll + (i * cellsize))]

                    # Store longitude values as array for use in row for loop (column number and relative DNI/GHI value for that row)
                    long_column_index = long_vals_diff[min(long_vals_diff)]
                
                # print(yul - (row_no * cellsize))
                lat_vals_diff[abs(lat - (yul - (row_no * cellsize)))] = [
                    dt, # Datetime value for this datapoint (based on filename)
                    float(row[long_column_index[0]]), # Closest DNI/GHI Value
                    round(float(yul - (row_no * cellsize)), 7), # Closest Lat Point
                    round(long_column_index[1], 6) # Closest Long Point
                ]

                # Increment row no
                row_no += 1
    
    # Return values as array:
    # [DNI/GHI value at closest lat/long, closest latitude, closest longitude]
    return lat_vals_diff[min(lat_vals_diff)]

# Main Loop
if __name__ == "__main__":
    # Print some data about this script
    print("\n" + "-" * 30)
    print("DNI/GHI Processing script")
    print("-" * 30)
    print('''
Takes user input for latitude and longitude and creates two CSV files
for the DNI and GHI values for that location for the nearest coordinate
found.

For this script to function the following folder/file structure must be present:
+-- DNI-YYYY
|   +-- solar_dni_YYYYMMDD_HHUT.txt
|   +-- ...
+-- GHI-XXXX
|   +-- solar_ghi_YYYYMMDD_HHUT.txt
|   +-- ...

YYYY is the year with century representaiton, eg 2013
MM is the zero-padded month value, eg 01 for January
DD is the zero-padded day of the month, eg 01 for the 1st
HH is the zero-padded hour (24 hour clock) of the day, eg 00, 13 for 12:00AM, 01:00PM
UT represents universal time, this script attempt to find the local timezone for the given
latitude and longitude to convert the UTC time to local time
''')

    try:
        tz = TimezoneFinder(in_memory=True)
    except:
        print("Timezone Finder Error - exiting")
        exit()

    # Get Lat and Long value from user input
    try:
        lat_input = float(input("Enter Latitude: "))
        lon_input = float(input("Enter Longitude: "))
    except:
        print("Invalid lat or long value!")
        exit()
    # Get year input
    try:
        year = int(input("Year: "))
        if len(str(year)) != 4: raise Exception()
    except:
        print("Invalid year, make sure you enter the 4 digit century value, eg 2013")
        exit()

    # Debug print CPU cores available
    if debug == 1: print("Available CPU Cores:{}".format(max_processes))

    # Time script to calculate how long script takes to run
    start_time = datetime.now()

    # Debug printing
    if debug == 2: print("You entered: ({}, {})".format(lat_input, lon_input))

    for directory in dir_names:
        # Read filenames from directories and store in list
        try:
            files = [["{}-{}/{}".format(directory.upper(),year,i.name), lat_input, lon_input] for i in os.scandir("{}-{}".format(directory.upper(), year))]
        except WindowsError as e:
            if e.winerror == 3:
                print("No DNI/GHI data folder for year {}, check that direcory exists.".format(year))
                exit()
            else:
                print(e)
                exit()

        # Create processes for DNI processing
        og_sign_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        p = Pool(processes=max_processes)
        signal.signal(signal.SIGINT, og_sign_handler)
        print("\nProcessing {} files:".format(directory)) # Print the current processing directory
        data = list(tqdm(p.imap_unordered(process_file, files), total=len(files), smoothing=0.5, ncols=100, dynamic_ncols=True))
        p.close()

        # Sort the values as they may be out of order from multiprocessing
        data.sort()

        # Get Local timezone
        tz_found = False
        try:
            if debug >= 1:
                # Debug print closest lat and long
                print("Closest Lat: {}".format(data[0][2]))
                print("Closest Lng: {}".format(data[0][3]))
            local_timezone = pytz.timezone(tz.timezone_at(lat=data[0][2],lng=data[0][3]))
            tz_found = True
        except:
            print("Couldn't find local timezone for the coordinates:")
            print("Latitude: {}".format(data[0][2]))
            print("Longitude: {}".format(data[0][3]))

        # Write csv file
        with open("{},{}_{}.csv".format(lat_input, lon_input,directory), 'w', newline='') as csv_obj:
            csv_wr = csv.writer(csv_obj)
            if tz_found:
                csv_wr.writerow(("UTC Time", "Local Time {}".format(local_timezone), "{} Value".format(directory.upper()), "Closest Latitude:",data[0][2], "Closest Longitude:",data[0][3]))
            else:
                csv_wr.writerow(("UTC Time", "Local Time UNKNOWN", "{} Value".format(directory.upper()), "Closest Latitude:",data[0][2], "Closest Longitude:",data[0][3]))
            for f in data:
                utc_time = f[0]
                if tz_found:
                    local_time = utc_time.astimezone(pytz.timezone(tz.timezone_at(lat=f[2],lng=f[3])))
                    csv_wr.writerow([utc_time.replace(tzinfo=None), local_time.replace(tzinfo=None), f[1]])
                else:
                    csv_wr.writerow([utc_time.replace(tzinfo=None), "", f[1]])


    print("Completed in {} seconds".format(datetime.now() - start_time))