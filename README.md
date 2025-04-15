# Occlusion Simulation
This project plots and simulates occlusion effects for measured impedances.

# Model
The project is based on a simplified model of the human outer ear:

![Lumped element model of the outer ear](/img/outer_ear_lem.png)

- *Volume Velocity Source*: Represents the vibrating ear canal walls
- *$Z_{tm}$*: Tympanic Membrane Acoustic Impedance
- *$Z_{EC}$*: EC Entrance Acoustic Impedance
- *$K_u$ and $K_d$: EC sections modeled as transmission lines

# Folder Structure
### Measurements
Each collection of measurements is stored in a subfolder. The subfolder's name is taken as the `label` property for plotting. The `no_include` folder stores measurement collections that should be ignored. A subfolder contains the measurements and a `config.json`.

`config.json` contains:
- `"color"`: plot color in hex
- `"linestyle"`: Matplotlib linestyle

### Reference
Contains a `no_include` folder and all open ear radiation impedances. Upon running the script, one can select a reference to use.

### Occlusion Data
Has the same structure as `Measurements`, but already contains occlusion plots instead of raw impedances. Bypasses the model, but can be used for comparinsons with literature data.

# Plotting
Enabling plots and setting properties can be done in `figures.json`.

- `show`: `true/false` -> Enables/disables the plot
- `include_open_ear`: `true/false` -> Weather the open ear reference should be included in the plot
- `include_perf_occl`: `true/false` -> Weather perfect occlusion should be included in the plot as reference
- `ylim`: `[y0, y1]` -> ylims of the plot
- - `include_open_ear`: `"outer"/"inner"` -> Weather the legend should be plotted inside or next to the plot

