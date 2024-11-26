# Lumerical and IPKISS Example
The files in this respository are an example to help kickstart Lumerical users who are looking to utilize the connect with IPKISS. 

## Prerequisites
- Ansys [Lumerical MODE](https://simutechgroup.com/ansys-software/optical/ansys-lumerical-mode/)
- [IPKISS](https://academy.lucedaphotonics.com/training/getting_started/0_installation/install_windows#install-windows)
- Optional: [PyCharm](https://academy.lucedaphotonics.com/tutorials/environment_setup/download_install_ide)

## Features
1. Basic PCells (Bragg Grating)
   - Generating Geometries
   - Parameterized Attributes
   - Declaring Ports
   - Exporting to GDS
   - Visualize topdown and cross-section (in console)
   - Generate Lumerical EME simulation
2. Advance PCells (Contradirectional Coupler)
   - Generate Geometries from Basic PCells
   - Declaring Ports in Nested PCells
   - Export to GDS
   - Generate Lumerical EME simulation
   - Export and Load S-Parameter Files
   - Device Transmission in IPKISS
3. Circuit Design File (Grating Couplers + ContraDC)
   - Instancing, placing, and connectiong PCells
   - Circuit Simulation
   - Cicuit Transmission in IPKISS
   - Export to GDS
