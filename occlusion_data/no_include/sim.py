#%%
import os
import re
import csv
import json

import numpy as np
import pyfar as pf
import matplotlib.pyplot as plt
import pyabsorp as pa
import matplotlib.patches as mpatches

from numpy import pi

## Select what to plot:
# Read figures configuration from figures.json
with open('figures.json', 'r') as f:
    figures = json.load(f)

# Constants
c = 343
rho0 = 1.2
temp = 23
hum = 37
atm = 101320

# Medium impedance
Z0 = rho0*c

# Ear canal dimensions
l_ec = 27.7e-3  # m
r_ec = 3.85e-3  # m
l_c = 8e-3      # m
l_u = l_c
l_d = l_ec-l_c
S_ec = pi*r_ec**2

# Init measurements dict
measurements = {}
occl_plots = {}
Z_ref = None
freq_range = [100, 1500]
frequencies = np.array([])

def read_frequency_csv(file_path):
    """
    Reads a CSV file containing a freqency vector and corresponding complex measurement data.

    Parameters:
    - file_path (str): Path to the CSV file.

    Returns:
    - pf.FrequencyData: The data in Pyfar format
    """
    freqVec = []
    freqDat = []
    
    # Regular expression to extract the real part from the frequency column
    # This assumes the frequency column is always in the form 'number+0i' or 'number-0i'
    freq_pattern = re.compile(r'^([-+]?\d*\.?\d+)(?:[+-]0i)$', re.IGNORECASE)
    
    # Open and read the CSV file
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row_num, row in enumerate(reader, start=1):
            if len(row) != 2:
                raise ValueError(f"Row {row_num} does not have exactly two columns: {row}")
            
            # Process the frequency column
            freq_str = row[0].strip()
            freq_match = freq_pattern.match(freq_str)
            if not freq_match:
                raise ValueError(f"Invalid frequency format in row {row_num}: '{freq_str}'")
            freq_real = float(freq_match.group(1))
            freqVec.append(freq_real)
            
            # Process the measurement column
            dat_str = row[1].strip()
            # Replace 'i' with 'j' for Python complex numbers
            dat_str_python = dat_str.replace('i', 'j')
            if 'j' in dat_str_python:
                try:
                    dat_complex = complex(dat_str_python)
                except ValueError as e:
                    raise ValueError(f"Cannot parse into complex number {row_num}: '{dat_str}'") from e
                freqDat.append(dat_complex)
            else:
                print(f'Cannot interpret data as complex, interpreting as dB values instead...')
                dat_complex = 10 ** (float(dat_str) / 20)
                dat_complex = complex(dat_complex, 0)
                freqDat.append(dat_complex)
    
    # Convert lists to NumPy arrays for better performance and usability
    freqVec = np.array(freqVec, dtype=np.float64)
    freqDat = np.array(freqDat, dtype=np.complex128)

    data = pf.FrequencyData(freqDat, freqVec)
    
    return data

def eardrum_impedance(frequencies):
    # after Shaw & Stinson (1983)
    # parameters given in Fig. 7 in Schroeter & Pösselt (1986)
    # Implementation taken from Kersten et. al (2024), DOI: 10.1121/10.0024244
    omega = 2*np.pi*frequencies
    iomega = 1j*omega
    K = 9
    L_a = 2e3
    R_a = 1e6
    C_p = 5.1e-11
    C_t = 3.5e-12
    R_m = 2e7
    C_do = 2e-12
    R_do = 1.7e7
    L_d = 1.2e3
    C_d = 3e-11
    R_d = 1e6
    L_o = 3e5
    C_o = 1.5e-13
    R_o = 9e8
    C_s = 2.7e-14
    R_s = 3e10
    L_c = 2e5
    C_c = 5e-14
    R_c = 6e9
    
    # calculations
    Z_ap = 1/(iomega*C_p) + iomega*L_a + R_a
    Z_cav = 1/(1/Z_ap + iomega*C_t + 1/R_m)
    Z_do = R_do + 1/(iomega*C_do)
    Z_d = R_d + iomega*L_d + 1/(iomega*C_d)
    Z_s = R_s + 1/(iomega*C_s)
    Z_c = R_c + iomega*L_c + 1/(iomega*C_c)
    Z_sc = 1/(1/Z_s + 1/Z_c)
    Z_o = R_o + iomega*L_o + 1/(iomega*C_o) + Z_sc
    Z_K = (Z_o*Z_do + Z_o*Z_d + K*K*Z_do*Z_d)/(Z_o+Z_d+(1+K)**2*Z_do)
    Z_eardrum = Z_cav + Z_K
    return pf.FrequencyData(Z_eardrum, frequencies)

## Acoustic Transmission line (pressure, volume velocity) for given length, crossectional area, and medium impedance
def acoustic_transmission_line(k, length, Area, frequencies, Z_eq = Z0):
    A = np.cos(k*length)
    B = 1j*(Z_eq/Area)*np.sin(k*length)
    C = 1j/(Z_eq/Area)*np.sin(k*length)
    D = np.cos(k*length)

    return pf.TransmissionMatrix.from_abcd(A, B, C, D, frequencies)

def read_measurements():
    '''
    This function reads all impedance measurements in the 'measurements' folder.
    - Each subfolder represents one measurement campaign
    '''
    global measurements, freq_range, S_ec, frequencies

    measurements_folder = './measurements'
    if not os.path.exists(measurements_folder):
        print(f'ERROR: Measurements folder not found')
        return
    
    for subfolder in os.listdir(measurements_folder):
        subfolder_path = os.path.join(measurements_folder, subfolder)
        
        if not os.path.isdir(subfolder_path) or subfolder == 'no_include':
            continue
        
        measurements[subfolder] = {}
            
        for file in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, file)
            if file == 'config.json':
                try:
                    with open(file_path, 'r') as conf_raw:
                        conf = json.load(conf_raw)
                        measurements[subfolder]['conf'] = conf
                except Exception as e:
                    print(f'Error reading config')
            if file.endswith('.csv'):
                try:
                    freqObjRaw = read_frequency_csv(file_path = file_path)

                    frequenciesRaw = freqObjRaw.frequencies
                    freqsRaw = freqObjRaw.freq[0]

                    mask = (frequenciesRaw >= freq_range[0]) & (frequenciesRaw <= freq_range[1])

                    frequenciesNew = frequenciesRaw[mask]
                    freqs = freqsRaw[mask]

                    if not np.array_equal(frequencies, frequenciesNew):
                        print(f'WARNING: Frequencies of {file} differ from reference. Interpolating....')
                        freqs = np.interp(frequencies, frequenciesNew, freqs)
                        frequenciesNew = frequencies


                    freq_data = pf.FrequencyData(freqs / S_ec, frequencies = frequenciesNew)

                    key = os.path.splitext(file)[0]
                    measurements[subfolder][key] = freq_data

                    print(f"Processed: {file}")
                except Exception as e:
                    print(f"ERROR: Couldn't read {file} as FrequencyData")
                    print(e)

def read_reference():
    '''
    This function reads the open ear reference impedance
    - If only one impedance is present, it will be chosen automatically
    - If multiple are present, the program will promt to chose one befor plotting
    '''
    global Z_ref, frequencies

    ref_folder = './reference'
    if not os.path.exists(ref_folder):
        print(f'ERROR: Reference folder not found')
        return
    
    files = [ file for file in os.listdir(ref_folder) if file.endswith('.csv') ]
    if not files:
        print(f'ERROR: No valid reference files (.csv)')

    print('Select an open ear canal radiation impedance as reference')
    for i, file in enumerate(files):
        print(f'{i+1}: {file}')
    
    while True:
        try:
            if len(files) == 1:
                choice = 1
            else:
                choice = int(input(f'Select a referece by number: '))
            if 1 <= choice <= len(files):
                sel_file = files[choice-1]
                print(f'{sel_file} selected')

                freqObjRaw = read_frequency_csv(file_path = os.path.join(ref_folder, sel_file))
                
                frequenciesRaw = freqObjRaw.frequencies
                freqsRaw = freqObjRaw.freq[0]

                mask = (frequenciesRaw >= freq_range[0]) & (frequenciesRaw <= freq_range[1])

                frequenciesNew = frequenciesRaw[mask]
                freqs = freqsRaw[mask]

                if np.array_equal(frequencies, []):
                    frequencies = frequenciesNew
                
                Z_ref = pf.FrequencyData(freqs / S_ec, frequencies = frequenciesNew)
                return

            else:
                print(f'ERROR: Enter a number between 1 and {len(files)}')
        except ValueError:
            print(f'ERROR: Enter a number between 1 and {len(files)}')

def read_occlusion_data():
    '''
    This function reads reference occlusion effect data to compare to the simulation
    '''
    global occl_plots, freq_range, frequencies

    occl_plots_folder = './occlusion_data'
    if not os.path.exists(occl_plots_folder):
        print(f'MESSAGE: Occlusion data folder not found, continuing without')
        return
    
    for subfolder in os.listdir(occl_plots_folder):
        subfolder_path = os.path.join(occl_plots_folder, subfolder)
        
        if not os.path.isdir(subfolder_path) or subfolder == 'no_include':
            continue
        
        occl_plots[subfolder] = {}
    
        for file in os.listdir(subfolder_path):
            file_path = os.path.join(subfolder_path, file)
            if file == 'config.json':
                try:
                    with open(file_path, 'r') as conf_raw:
                        conf = json.load(conf_raw)
                        occl_plots[subfolder]['conf'] = conf
                except Exception as e:
                    print(f'Error reading config')
            if file.endswith('.csv'):
                try:
                    freqObjRaw = read_frequency_csv(file_path = file_path)

                    frequenciesRaw = freqObjRaw.frequencies
                    freqsRaw = freqObjRaw.freq[0]

                    mask = (frequenciesRaw >= freq_range[0]) & (frequenciesRaw <= freq_range[1])

                    frequenciesNew = frequenciesRaw[mask]
                    freqs = freqsRaw[mask]

                    if not np.array_equal(frequencies, frequenciesNew):
                        print(f'WARNING: Frequencies of {file} differ from reference. Interpolating....')
                        freqs = np.interp(frequencies, frequenciesNew, freqs)
                        frequenciesNew = frequencies


                    freq_data = pf.FrequencyData(freqs , frequencies = frequenciesNew)

                    if 'mean' in os.path.splitext(file)[0]:
                        key = 'mean'
                    elif 'std' in os.path.splitext(file)[0]:
                        key = 'std'
                    else:
                        continue
                        
                    occl_plots[subfolder][key] = freq_data

                    print(f"Processed: {file}")
                except Exception as e:
                    print(f"ERROR: Couldn't read {file} as FrequencyData")
                    print(e)

def ear_muff_simulation(l_cup, l_abs, S_cup, S_abs, k_cup, k_abs, Z_cup, Z_abs, frequencies):
    global pinna_offset #= pf.FrequencyData(frequencies*0+10**(7/20), frequencies)  # Pinna has 7dB offset to open end (Schüring, Rohr mit Ohr)

    TL_cup = acoustic_transmission_line(k_cup, l_cup, S_cup, frequencies, Z_cup)
    TL_abs = acoustic_transmission_line(k_abs, l_abs, S_abs, frequencies, Z_abs)
    TL_pin = acoustic_transmission_line(k, 0.01, 0.02**2, frequencies)

    Z_load_sim = TL_pin.input_impedance( TL_cup.input_impedance( TL_abs.input_impedance( Z_inf ) ) )
    return ( Z_load_sim, ( pf.TransmissionMatrix.create_shunt_admittance( 1 / (K_u.input_impedance( Z_load_sim ) * pinna_offset) ) @ K_d ).transfer_function( (1, 1), Z_tm ) )

#%%
read_reference()
read_measurements()
read_occlusion_data()

# Pinna Offset
pinna_offset = pf.FrequencyData(frequencies*0+10**(7/20), frequencies)

# Wave numbers
omega = 2*pi*frequencies
k = 2*pi*frequencies / c

# Upstream (to exit) and downstream (to TM) sections of ear canal as transmission lines
K_u = acoustic_transmission_line(k, l_u, S_ec, frequencies)
K_d = acoustic_transmission_line(k, l_d, S_ec, frequencies)

#%%
###########################
##    EC Impedances      ##
###########################
Z_tm = eardrum_impedance(frequencies = frequencies)                 # Tympanic membrane impedance
Z_inf = pf.FrequencyData(np.inf*frequencies, frequencies)     # Perfectly occluded with infinite impedance

# %%
###########################
##    Transfer Funcs     ##
###########################
T_ref = ( pf.TransmissionMatrix.create_shunt_admittance( 1 / K_u.input_impedance( Z_ref ) ) @ K_d ).transfer_function( (1, 1), Z_tm )
T_occl_perf = ( pf.TransmissionMatrix.create_shunt_admittance( 1 / K_u.input_impedance( Z_inf ) ) @ K_d ).transfer_function( (1, 1), Z_tm )
T_meas_projects = [ (collection_key, measurements[collection_key]['conf'], [ (key, ( pf.TransmissionMatrix.create_shunt_admittance( 1 / K_u.input_impedance( measurements[collection_key][key] ) ) @ K_d ).transfer_function( (1, 1), Z_tm )) for key in measurements[collection_key] if key != 'conf']) for collection_key in measurements ]

# %%
###########################
##         Box           ##
###########################
## Data from 'Reduction of the occlusion effect induced by earplugs using quasi perfect broadband absorption', Carillo et. al. 2022
visc = 1.83e-5        # dynamic viscosity
heats = 1.4           # specific heats ratio
Cp = 1.002e3          # heat capacity at constant pressure
therm_cond = 0.025    # themal conductivity
Pr = 0.707            # Prandtl number
poros = 0.9          # porosity
tortu = 1.1           # tortuosity
resis = 26000         # air flow resistivity    
visc_l = 8.7e-5       # viscous characteristic length
therm_l = 1.63e-4     # thermal characteristic length

Z_eq, k_eq = pa.johnson_champoux(resis, rho0, poros, tortu, heats, Pr, atm, visc_l, therm_l, visc, therm_cond, Cp, frequencies, var = 'allard')

Z_box1, T_box1 = ear_muff_simulation(0.1, 0.05, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)
Z_box2, T_box2 = ear_muff_simulation(0.075, 0.075, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)
Z_box3, T_box3 = ear_muff_simulation(0.05, 0.1, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)

Z_box4, T_box4 = ear_muff_simulation(0.15, 0.15, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)
Z_box5, T_box5 = ear_muff_simulation(0.1, 0.1, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)
Z_box6, T_box6 = ear_muff_simulation(0.05, 0.15, 0.0027, 3.5e-3, k-1j*6*10**(-2)*np.sqrt(frequencies / (c*(0.0027/pi))), k_eq, Z0, Z_eq, frequencies)


T_boxes = [
    (Z_box1, T_box1, 'l_ext = 10cm, l_foam = 5cm', '#cc071e', '-'), 
    (Z_box2, T_box2, 'l_ext = 7.5cm, l_foam = 7.5cm', '#57ab27', '-'),
    (Z_box3, T_box3, 'l_ext = 5cm, l_foam = 10cm', '#00549f', '-'), 
    (Z_box4, T_box4, 'l_ext = 15cm, l_foam = 5cm', '#cc071e', '--'),
    (Z_box5, T_box5, 'l_ext = 10cm, l_foam = 10cm', '#57ab27', '--'), 
    (Z_box6, T_box6, 'l_ext = 5cm, l_foam = 15cm', '#00549f', '--'), 
]
# %%
###########################
##         Plots         ##
###########################

## Figure 1: Transfer Functions
if figures['fig1']['show']:
    plt.figure(1)
    plt.title('Transfer functions between EC wall and TM')

    if figures['fig1']['include_open_ear']:
        pf.plot.freq(T_ref, label = 'Open ear (reference measurement)', color = '#f6a800', linestyle = ':')
    
    if figures['fig1']['include_perf_occl']:
        pf.plot.freq(T_occl_perf, label = 'Perfectly occluded (Z=inf)', color = '#4f9d69', linestyle = '-.')
    
    for T_box in T_boxes:
        ax = pf.plot.freq( T_box[1], label = T_box[2], color = T_box[3], linestyle = T_box[4])

    for (_, conf, T_measurements) in T_meas_projects:
        for (collectionkey, T) in T_measurements:
            pf.plot.freq(T, label = collectionkey, color = conf['color'], linestyle = conf['linestyle'])

    ax.set_ylim(figures['fig1']['ylim'][0], figures['fig1']['ylim'][1])
    
    if figures['fig1']['loc_legend'] == 'inner':
        plt.legend(loc='lower right')
    elif figures['fig1']['loc_legend'] == 'outer':
        plt.legend(bbox_to_anchor=(1.05, 1.03), loc = 'upper left')

## Figure 2: Occlusion Effect
if figures['fig2']['show']:
    plt.figure(2)
    plt.title('Estimated occlusion effect (vs reference measurement)')

    if figures['fig2']['include_open_ear']:
        pf.plot.freq( T_ref / T_ref, label = 'Reference: Open ear canal (no occlusion)', color = '#f6a800', linestyle = ':')
    
    if figures['fig2']['include_perf_occl']:
        pf.plot.freq( T_occl_perf / T_ref, label = 'Perfectly occluded (Z = inf)', color = '#4f9d69', linestyle = '-.')

    for (_, conf, T_measurements) in T_meas_projects:
        for (collectionkey, T) in T_measurements:
            ax = pf.plot.freq( T / T_ref, label = collectionkey, color = conf['color'], linestyle = conf['linestyle'])

    for key in occl_plots:
        mean = occl_plots[key]['mean']
        std = occl_plots[key]['std']
        color = occl_plots[key]['conf']['color']
        linestyle = occl_plots[key]['conf']['linestyle']
        
        pf.plot.freq(mean, label = key, color = color, linestyle = linestyle)
        plt.fill_between( frequencies, 20*np.log10((mean-std).freq[0]), 20*np.log10((mean+std).freq[0]), color = color, alpha=0.2 )
    
    ax.set_ylim(figures['fig2']['ylim'][0], figures['fig2']['ylim'][1])
    
    if figures['fig2']['loc_legend'] == 'inner':
        plt.legend(loc='lower right')
    elif figures['fig2']['loc_legend'] == 'outer':
        plt.legend(bbox_to_anchor=(1.05, 1.03), loc = 'upper left')

## Figure 3: Occlusion Effect mean and std of measurement folder
if figures['fig3']['show']:
    plt.figure(3)
    plt.title('Estimated Occlusion Gain') #occlusion effect (mean and std of measurement folder)')
    
    if figures['fig3']['include_open_ear']:
        pf.plot.freq( T_ref / T_ref, label = 'Reference: Open ear canal (no occlusion)', color = '#f6a800', linestyle = ':')
    if figures['fig3']['include_perf_occl']:
        pf.plot.freq( T_occl_perf / T_ref, label = 'Perfectly occluded (Z = inf)', color = '#4f9d69', linestyle = '-.')
        
    for (collectionkey, conf, T_measurements) in T_meas_projects:
        mean = pf.FrequencyData(sum(abs(sig.freq[0]) for (_, sig) in T_measurements) / len(T_measurements), frequencies)
        std = pf.FrequencyData(np.sqrt(sum(( abs(sig.freq[0]) - abs(mean.freq[0])) ** 2 for (_, sig) in T_measurements) / len(T_measurements)), frequencies)

        # Export mean as CSV
        #mean_csv_path = f"output/mean_{collectionkey}.csv"
        #with open(mean_csv_path, "w", newline="") as csvfile:
        #    writer = csv.writer(csvfile)
        #    writer.writerow(["Frequency (Hz)", "Mean"])
        #    for f, m in zip(frequencies, mean.freq[0]):
        #        writer.writerow([f, m])

        ax = pf.plot.freq(mean / T_ref, label = f'{collectionkey} mean and std', color = conf['color'], linestyle = conf['linestyle'])
        plt.fill_between( frequencies, 20*np.log10(((mean-std) / T_ref).freq[0]), 20*np.log10(((mean+std) / T_ref).freq[0]), color = ax.lines[-1].get_color(), alpha=0.2 )
    
    for key in occl_plots:
        mean = occl_plots[key]['mean']
        std = occl_plots[key]['std']
        color = occl_plots[key]['conf']['color']
        linestyle = occl_plots[key]['conf']['linestyle']
        ax = pf.plot.freq( mean, label = f'{key}', color = color, linestyle = linestyle, alpha = 0.2, linewidth = 5)
        #plt.fill_between( frequencies, 20*np.log10((mean-std).freq[0]), 20*np.log10((mean+std).freq[0]), color = color, alpha=0.2 )
    
    ax.set_ylim(figures['fig3']['ylim'][0], figures['fig3']['ylim'][1])
    
    if figures['fig3']['loc_legend'] == 'inner':
        plt.legend(loc='lower right')
    elif figures['fig3']['loc_legend'] == 'outer':
        plt.legend(bbox_to_anchor=(1.05, 1.03), loc = 'upper left')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
## Figure 4: EC Load Impedances
if figures['fig4']['show']:
    plt.figure(4)
    plt.title('Simulated Load Impedances')
    
    if figures['fig4']['include_open_ear']:
        pf.plot.freq( K_u.input_impedance(Z_ref), color = '#f6a800', linestyle = ':', label = 'open ear')
    
    for Z_load, _, label, color, linestyle in T_boxes:
       ax = pf.plot.freq( K_u.input_impedance(Z_load) * pinna_offset, color = 'lightgray', linestyle = linestyle)

    for collection_key in measurements:
        mean = pf.FrequencyData(sum(abs(K_u.input_impedance(measurements[collection_key][key]).freq[0]) for key in measurements[collection_key] if key != 'conf') / ( len(measurements[collection_key]) - 1 ), frequencies)
        std = pf.FrequencyData(np.sqrt(sum(( abs(K_u.input_impedance(measurements[collection_key][key]).freq[0]) - abs(mean.freq[0])) ** 2 for key in measurements[collection_key] if key != 'conf') / ( len(measurements[collection_key]) - 1 )), frequencies)
        color = measurements[collection_key]['conf']['color']
        linestyle = measurements[collection_key]['conf']['linestyle']
               
        ax = pf.plot.freq(mean, label = f'Mean (bold) and std (shade) of {collection_key}', color = color, linestyle = linestyle)
        plt.fill_between( frequencies, 20*np.log10((mean-std).freq[0]), 20*np.log10((mean+std).freq[0]), color = color, alpha=0.2 )     
    
    ax.set_ylim(figures['fig4']['ylim'][0], figures['fig4']['ylim'][1])
    
    handles, labels = ax.get_legend_handles_labels()
    patch = mpatches.Patch(color='lightgray', label='Simulations')
    handles.append(patch) 
    
    if figures['fig4']['loc_legend'] == 'inner':
        plt.legend(handles=handles, loc='lower right')
    elif figures['fig4']['loc_legend'] == 'outer':
        plt.legend(handles=handles, bbox_to_anchor=(1.05, 1.03), loc = 'upper left')
    
plt.show()
# %%
