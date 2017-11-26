<p align="center">
<a href="#features">Features</a> |
<a href="#requirements">Requirements</a> |
<a href="#documentation">Documentation</a> |
<a href="#usage">Usage</a> |
<a href="#communication">Communication</a>
</p>

# Sizing residential PV battery systems
<br />
Python code for sizing PV battery systems.


## Features

Calculate:
- Energy Directly used (Edu)
- Energy Used for charging the battery (Ebc)
- Grid Consumption
- Ebd Energy Battery Discharge
- Self-consumption rate
- Plot final data
- Creates file with final data
- Grid feed-in
- Degree of self-sufficiency (d)

## Requirements

- Python 2.7+
- Matplotlib
- xlrd (for excel examples)

## Documentation

- Docs: [https://docs.python.org/2.7/](url)
- matplotlib: [https://matplotlib.org/users/installing.html](url)


## Usage

Installation. In case of Linux or Mac, open terminal:
- $ sudo easy_install pip
- $ sudo pip install xlrd
- $ python -mpip install -U pip
- $ python -mpip install -U matplotlib

Download
- $ cd Downloads/
- $ git clone https://github.com/al3Co/Python-Codes.git

Run
- $ cd SizingResidentialPVbatterysystems/
- $ python batterySim.py

Running
- You need to write the name of the .xlsx file
- The .xlsx file must contain 3 columns called: Time, Consumption (W) and PV generation
- You need to write the price of the trading of Energy
- This code have to be at the same folder of the .xlsx file


## Communication

- If you found a bug, please open an issue
- Also, if you have a feature request, please open an issue
- If you want to contribute, submit a pull request
- Contact: raquel.vasquezt@gmail.com

