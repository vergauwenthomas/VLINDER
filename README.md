# VLINDER
A collection of applications on VLINDER


## required packages
The required packages and python version are combined in a conda enviroment that can be created using the `enviroment.yml` file. Make sure a Conda client is installed and install the `geo_env` using:
- `conda env create -f envioment.yml`
and activating with `conda activate geo_env`

## Path handler
This script manages the paths and links to other scripts. Before you run any script, make sure you uncomment your name so the paths are suitable for your local machine. (The path-handling should be able to handle all OS's)

## Data folder
This folder contains the data that is often used i.e. Vlinder location and identifier data

## Dashboard_visuals
This folder contains all the scripts that generate data or visuals that are used in the VLINDER-dashboard. 

## Meta_data_script
Here you can find a script that calculates the meta data (landcover, height, lcz) for a given location. Adjust the data file in this folder and execute the script. The output will appear in the folder. 

## Mbilli_code
Here you can find a version of the software on the VLINDER stations (V12)

