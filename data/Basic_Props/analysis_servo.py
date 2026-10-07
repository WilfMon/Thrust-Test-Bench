import csv
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

data = "tst.csv"

with open(data, mode='r', newline='') as file:
    reader = csv.reader(file)
    
    speed = []
    servo = []
    power = []
    thrust = []
    current = []
    voltage = []
    
    for row in reader:
        clean_row = row[0].split(",")
        
        if clean_row[2] == "NA":
            clean_row[2] = 0
        
        speed.append(float(clean_row[0]))
        servo.append(float(clean_row[1]))
        power.append(float(clean_row[2]))
        thrust.append(- float(clean_row[3]))
        current.append(float(clean_row[4]))
        voltage.append(float(clean_row[5]))
        
ax.plot(servo, thrust)

plt.show()