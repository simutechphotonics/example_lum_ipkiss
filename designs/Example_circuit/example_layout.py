from si_fab import all as pdk
from ipkiss3 import all as i3
from designs.ContraDC import ContraDirectionCoupler as CDC

#Initiate the devices
CDC = CDC.ContraDC()
GC = pdk.GratingCoupler(
    line_width=0.83,
    period=1.2,
    n_o_periods=15,
)

# Create an instance cell of the required devices
insts = {
    "CDC":CDC,
    "GC1": GC,
    "GC2": GC,
    "GC3": GC,
    "GC4": GC,
}

# Place and join the cells to create the device
specs = [
    i3.Place("CDC", (50, 127*1.5),angle=90),
    i3.Place("GC1",(0,0)),
    i3.Place("GC2", (0, 127)),
    i3.Place("GC3", (0, 127*2)),
    i3.Place("GC4", (0, 127*3)),

    i3.ConnectBend("GC1:out","CDC:Port1"),
    i3.ConnectBend("GC2:out","CDC:Port2"),
    i3.ConnectBend("GC3:out","CDC:Port4"), #prevent an waveguide crossing
    i3.ConnectBend("GC4:out","CDC:Port3"),
]

exposed_port_names = {
    'GC1:vertical_in': 'Port1',
    'GC2:vertical_in': 'Port2',
    'GC3:vertical_in': 'Port3',
    'GC4:vertical_in': 'Port4',
}

# Instantiate the i3.Circuit class to create the circuit.
my_circuit = i3.Circuit(
    name="example_layout",
    insts=insts,
    specs=specs,
    exposed_ports=exposed_port_names,
)

# Show the circuit and write to layout
my_circuit_layout = my_circuit.Layout()
my_circuit_layout.visualize(annotate=True) #Display in python
my_circuit_layout.write_gdsii("example_layout.gds") #create layout file

# Circuit model
import numpy as np
import matplotlib.pyplot as plt
wavelengths = np.linspace(1.52, 1.58, 4001)
#Grating Coupler
GC_cm = GC.CircuitModel(
    center_wavelength=1.55,
    bandwidth_1dB=0.03,
    peak_IL_dB = 0.6 ** 0.5,
    reflection=0.05 ** 0.5,
    reflection_vertical_in = 0.05 ** 0.5,
)
S_GC = GC_cm.get_smatrix(wavelengths=wavelengths)
S_GC.visualize(term_pairs=[("vertical_in", "out")])

#ContraDC
CDC_cm = CDC.CircuitModel()
wavelengths = np.linspace(1.5, 1.6, 201)
S_CDC = CDC_cm.get_smatrix(wavelengths=wavelengths)
S_CDC.visualize(
    term_pairs=[
        ("Port1", "Port2"),  # Through port
        ("Port1", "Port3"),  # Drop port
    ],
)

#Full Circuit
my_circuit_cm = my_circuit.CircuitModel() #initiate the circuit model
S_total = my_circuit_cm.get_smatrix(wavelengths=wavelengths) #get the smatrix and calculate the input wavelength
S_total.visualize(
    term_pairs=[
        ("Port1", "Port2"),  # Through port
        ("Port1", "Port4"),  # Drop port, Port 4 (GC) connected to Port 3 (CDC) to prevent a waveguide crossing in the layout
    ],
)

#To IPKISS Canvas
my_circuit_layout.to_canvas(project_name="Test_Circuit")