import csv
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_8X45 = "data/8X45_1818.csv"
_10X5E= "data/10X5E_1818.csv"

fig = make_subplots(specs=[[{"secondary_y": True}]])

for name, col, data in [("8X45", "blue", _8X45), ("10X5E", "red", _10X5E)]:
    with open(data, mode='r', newline='') as file:
        reader = csv.reader(file)
        
        speed = []
        power = []
        thrust = []
        for row in reader:
            clean_row = row[0].split(",")
            
            if clean_row[2] == "NA":
                clean_row[2] = 0
            
            speed.append(float(clean_row[0]))
            power.append(float(clean_row[1]))
            thrust.append(float(clean_row[2]))
            
        efficiency = np.array(thrust) / np.array(power)
            
        # 1. Plot the Power Line (Left Axis)
        fig.add_trace(
            go.Scatter(
                x=thrust, 
                y=power, 
                mode='lines+markers', 
                name=f"{name} Power",
                line=dict(color=col),
                hovertemplate=f"<b>{name}</b><br>Power: %{{y:.1f}}W<extra></extra>"
            ),
            secondary_y=False  # Maps to the left axis
        )
        
        # 2. Plot the Efficiency Line (Right Axis - Dashed)
        fig.add_trace(
            go.Scatter(
                x=thrust, 
                y=efficiency, 
                mode='lines', 
                name=f"{name} Efficiency",
                line=dict(dash='dash', color=col),
                hovertemplate=f"<b>{name}</b><br>Efficiency: %{{y:.2f}} g/W<extra></extra>"
            ),
            secondary_y=True  # Maps to the right axis
        )

# Apply Dark Theme and Fine-Tune Ticks
fig.update_layout(
    template="plotly_dark",
    title="Propeller Performance: Power & Efficiency vs Thrust",
    hovermode="x unified",  # Tracks all curves simultaneously at a given Thrust value
    
    # X-Axis Customization (Thrust)
    xaxis=dict(
        title="Thrust (g)",
        tickmode='linear',
        tick0=0,
        dtick=50,
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)'
    ),
    
    # Left Y-Axis Customization (Power)
    yaxis=dict(
        title="Power (W)",
        tickmode='linear',
        tick0=0,
        dtick=10,
        showgrid=True,
        gridcolor='rgba(255, 255, 255, 0.1)'
    ),
    
    # Right Y-Axis Customization (Efficiency)
    yaxis2=dict(
        title="Efficiency (g/W)",
        tickmode='linear',
        tick0=0,
        dtick=1,  # Tick marks every 1 g/W change
        showgrid=False  # Keep false so grid lines don't clash with the left axis
    )
)

fig.show()