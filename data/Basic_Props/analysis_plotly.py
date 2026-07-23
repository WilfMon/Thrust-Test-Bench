import csv
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_8X45 = "data/Basic_Props/8X45_1818.csv"
_10X5E= "data/Basic_Props/10X5E_1818.csv"

STEP = 5

fig = make_subplots(specs=[[{"secondary_y": True}]])

for name, col, data in [("8X45", "#00BFFF", _8X45), ("10X5E", "#FF0000", _10X5E)]:
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
        
        # generate a x step moving avarage for the power against thurst graph
        half_step = int(np.floor(STEP / 2))
        
        power_avg = []
        thrust_avg = []
        
        for i, point in enumerate(power):

            # generate lists of none valid i
            na = []
            for j in range(half_step):
                na.append(j)
                na.append(len(power) - 1 - j)

            # check for a valid i because moving avarage needs points around the point
            if i in na:
                pass
            
            else:
                # get the points bellow and above the current
                p_points = []
                t_points = []
                
                for k in range(STEP):
                    p_points.append(power[i - half_step + k])
                    
                for k in range(STEP):
                    t_points.append(thrust[i - half_step + k])
                
                # take an avarage
                pavg = np.mean(p_points)
                tavg = np.mean(t_points)
                
                # add this avarage to a list
                power_avg.append(pavg)
                thrust_avg.append(tavg)
                
        efficiency = np.array(thrust) / np.array(power)
        efficiency_avg = np.array(thrust_avg) / np.array(power_avg)
            
            
        # Plot the Power Avarage Line (Left Axis)
        fig.add_trace(
            go.Scatter(
                x=thrust_avg, 
                y=power_avg, 
                mode='lines+markers', 
                name=f"{name} Power",
                line=dict(color=col),
                hovertemplate=f"<b>{name}</b><br>Power: %{{y:.1f}}W<extra></extra>"
            ),
            secondary_y=False  # Maps to the left axis
        )
        
        # Plot the Power Line as translucent
        fig.add_trace(
            go.Scatter(
                x=thrust, 
                y=power, 
                mode='lines', 
                name=f"{name} Power",
                line=dict(color=col),
                opacity=0.4,
                hovertemplate=f"<b>{name}</b><br>Power: %{{y:.1f}}W<extra></extra>"
            ),
            secondary_y=False  # Maps to the left axis
        )
        
        # Plot the Efficiency Avarage  (Right Axis - Dashed)
        fig.add_trace(
            go.Scatter(
                x=thrust_avg, 
                y=efficiency_avg, 
                mode='lines', 
                name=f"{name} Efficiency",
                line=dict(dash='dash', color=col),
                hovertemplate=f"<b>{name}</b><br>Efficiency: %{{y:.2f}} g/W<extra></extra>"
            ),
            secondary_y=True  # Maps to the right axis
        )    
    
        # Plot the Efficiency
        fig.add_trace(
            go.Scatter(
                x=thrust, 
                y=efficiency, 
                mode='lines', 
                name=f"{name} Efficiency",
                line=dict(dash='dash', color=col),
                opacity=0.4,
                hovertemplate=f"<b>{name}</b><br>Efficiency: %{{y:.2f}} g/W<extra></extra>"
            ),
            secondary_y=True  # Maps to the right axis
        )

# Apply Dark Theme and Fine-Tune Ticks
fig.update_layout(
    template="plotly_dark",
    title=f"Propeller Performance: Power & Efficiency vs Thrust: {STEP} step moving avarage shown, raw data lower opacity",
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