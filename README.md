# Occlusion Simulation
This project plots and simulates occlusion effects for measured impedances.

# Model
The project is based on a simplified model of the human outer ear:

 <svg version="1.0" xmlns="http://www.w3.org/2000/svg"  width="300.000000pt" height="65.000000pt" viewBox="0 0 300.000000 65.000000"  preserveAspectRatio="xMidYMid meet">  <g transform="translate(0.000000,65.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none"> <path d="M1837 632 c-10 -10 -17 -35 -17 -55 l0 -37 -310 0 -310 0 0 34 c0 54 -26 66 -142 66 -111 0 -138 -14 -138 -70 l0 -30 -114 0 c-89 0 -116 3 -126 15 -14 17 -46 20 -55 5 -3 -6 -52 -10 -111 -10 l-104 0 0 -45 0 -45 -45 0 -44 0 0 -130 1 -130 44 0 44 0 0 -57 0 -58 100 3 c81 3 103 0 116 -12 20 -20 53 -21 60 -1 5 12 28 15 120 15 107 0 114 -1 114 -20 0 -11 9 -29 20 -40 17 -17 33 -20 118 -20 109 0 142 13 142 56 l0 24 308 0 308 0 11 -30 11 -30 115 0 c98 0 116 3 130 18 10 10 17 24 17 30 0 9 63 12 240 12 l240 0 0 95 0 95 30 0 c17 0 30 5 30 10 0 6 -33 10 -80 10 -47 0 -80 -4 -80 -10 0 -5 18 -10 40 -10 l40 0 0 -85 0 -85 -230 0 -230 0 0 205 0 205 225 0 225 0 0 -80 0 -80 -35 0 c-19 0 -35 -4 -35 -10 0 -6 35 -10 85 -10 50 0 85 4 85 10 0 6 -18 10 -40 10 l-40 0 0 90 0 90 -235 0 -235 0 0 39 c0 60 -22 71 -146 71 -85 0 -103 -3 -117 -18z m231 -14 c17 -17 17 -539 0 -556 -8 -8 -48 -12 -114 -12 -84 0 -103 3 -108 16 -3 9 -6 134 -6 278 0 190 3 265 12 274 16 16 200 16 216 0z m-899 -12 c8 -9 11 -94 9 -287 l-3 -274 -109 -3 c-81 -2 -112 1 -118 10 -4 7 -8 131 -8 275 0 225 2 264 16 277 21 21 196 23 213 2z m-549 -86 c0 -5 14 -10 30 -10 17 0 30 3 30 8 0 4 54 6 120 4 l120 -3 0 -206 0 -205 -144 3 c-79 2 -148 1 -152 -4 -4 -4 -49 -7 -101 -7 l-93 0 0 34 c0 19 -3 41 -6 50 -5 13 2 16 35 16 l41 0 0 130 0 130 -38 0 c-37 0 -38 1 -38 35 l1 35 98 0 c58 0 97 -4 97 -10z m900 -48 c0 -45 -2 -48 -32 -57 -62 -19 -91 -98 -58 -159 7 -15 31 -34 52 -43 35 -16 38 -20 38 -59 l0 -43 -156 -3 c-86 -2 -158 -1 -160 1 -2 2 -4 96 -4 208 l0 203 160 0 160 0 0 -48z m300 -159 l0 -208 -139 0 -139 0 -4 48 c-3 43 -1 48 20 54 39 10 72 59 72 110 0 36 -6 50 -29 74 -16 16 -37 29 -45 29 -12 0 -16 11 -16 50 l0 50 140 0 140 0 0 -207z m-1340 17 l0 -110 -65 0 -65 0 0 110 0 110 65 0 65 0 0 -110z m1115 37 c22 -31 19 -89 -5 -115 -47 -50 -128 -33 -150 32 -15 46 2 85 48 108 40 19 83 9 107 -25z"/> <path d="M1889 388 c-1 -2 -3 -25 -5 -51 -2 -34 0 -47 9 -44 7 2 12 9 12 15 0 21 14 23 25 3 6 -12 18 -21 26 -21 13 0 12 5 -5 28 -19 27 -19 30 -4 45 9 9 13 20 9 24 -4 5 -16 -2 -26 -14 -21 -26 -35 -30 -27 -8 4 8 2 17 -3 20 -6 4 -11 5 -11 3z"/> <path d="M1990 275 c0 -32 3 -36 23 -33 17 2 22 10 22 33 0 23 -5 31 -22 33 -20 3 -23 -1 -23 -33z"/> <path d="M990 325 c0 -25 5 -45 10 -45 6 0 10 9 10 20 0 11 4 20 9 20 5 0 13 -9 16 -20 3 -11 13 -20 21 -20 12 0 12 4 -2 25 -16 24 -16 27 1 45 23 25 0 28 -27 3 -17 -15 -18 -15 -18 0 0 10 -4 17 -10 17 -5 0 -10 -20 -10 -45z"/> <path d="M1092 263 c2 -20 9 -29 24 -31 17 -2 22 3 26 27 3 17 1 31 -4 31 -4 0 -8 -9 -8 -20 0 -11 -4 -20 -10 -20 -5 0 -10 9 -10 20 0 11 -5 20 -11 20 -6 0 -9 -12 -7 -27z"/> <path d="M1512 345 c-7 -15 -8 -25 -2 -25 6 0 10 -16 10 -35 0 -19 5 -35 10 -35 6 0 10 16 10 35 0 19 4 35 9 35 5 0 4 11 -2 25 -15 31 -21 31 -35 0z"/> <path d="M2710 369 c0 -6 9 -9 20 -6 11 3 20 2 20 -2 0 -5 -9 -16 -20 -26 -31 -28 -25 -45 15 -45 19 0 35 5 35 10 0 6 -9 10 -21 10 l-20 0 20 29 c28 39 27 41 -14 41 -19 0 -35 -5 -35 -11z"/> <path d="M80 360 c0 -5 9 -10 21 -10 19 0 19 -2 -7 -35 -14 -19 -25 -35 -23 -36 35 -5 79 -4 79 3 0 4 -12 8 -26 8 l-26 0 26 31 c34 40 33 49 -9 49 -19 0 -35 -4 -35 -10z"/> <path d="M2800 271 c0 -24 4 -31 19 -31 12 0 21 8 24 23 l4 22 2 -22 c1 -27 21 -31 22 -5 0 14 2 14 9 -3 8 -18 9 -17 9 8 1 23 -3 27 -28 27 -16 0 -36 3 -45 6 -13 5 -16 -1 -16 -25z"/> <path d="M180 230 c0 -25 4 -30 23 -29 16 1 18 2 5 6 -10 2 -18 9 -18 14 0 6 4 8 9 4 5 -3 12 -1 16 5 3 5 -2 10 -12 11 -16 0 -16 1 2 9 19 8 19 9 -2 9 -19 1 -23 -4 -23 -29z"/> <path d="M234 245 c-9 -23 3 -45 26 -45 11 0 20 5 20 10 0 6 -6 10 -13 8 -7 -2 -14 0 -15 5 -5 18 -1 26 13 21 8 -4 15 -1 15 5 0 17 -40 13 -46 -4z"/> </g> </svg> 

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

