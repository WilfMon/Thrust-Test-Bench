import csv
import numpy as np
import matplotlib.pyplot as plt

_8X45 = "data/Basic_Props/8X45_1818.csv"
_10X5E= "data/Basic_Props/10X5E_1818.csv"

fig, ax = plt.subplots()

for name, col, data in [("8X45", "blue", _8X45), ("10X5E", "red", _10X5E)]:
    with open(data, mode='r', newline='') as file:
        reader = csv.reader(file)
    
        speed = []
        power = []
        thrust = []
        current = []
        voltage = []
        for row in reader:
            clean_row = row[0].split(",")
            
            if clean_row[2] == "NA":
                clean_row[2] = 0
            
            speed.append(float(clean_row[0]))
            power.append(float(clean_row[1]))
            thrust.append(float(clean_row[2]))
            current.append(float(clean_row[3]))
            voltage.append(float(clean_row[4]))
            
        efficiency = np.array(thrust) / np.array(power)
        
    ax.plot(current, voltage, label=name, color=col)
    ax.set_xlabel("Current (A)")
    ax.set_ylabel("voltage (V)")

ax.legend()
plt.show()