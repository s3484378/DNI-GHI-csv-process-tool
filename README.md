# DNI-GHI-csv-process-tool
Command line script to convert DNI/GHI data into a csv file for a given latitude and longitude

## Description
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
