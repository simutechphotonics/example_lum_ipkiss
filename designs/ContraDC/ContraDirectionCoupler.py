from si_fab import all as pdk
from ipkiss3 import all as i3
#relative import of devices
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from designs.BraggStraight import BraggStraight as Bragg

class ContraDC(i3.PCell):
    """ContraDirection Coupler with 2 input and 2 output."""  # a short description of the class is always useful to include
    _name_prefix = "ContraDC"
    #trace_template = i3.TraceTemplateProperty(doc="Trace template of the access waveguide.") #template for the waveguide
    # Parameters
    period = i3.PositiveNumberProperty(default=0.324, doc="distance between a set of gratings. [um]")
    period_num = i3.PositiveIntProperty(default=100, doc="amount of periods.")
    dw1 = i3.NonNegativeNumberProperty(default=0.05, doc="corrugation width for wg1. [um]")
    dw2 = i3.NonNegativeNumberProperty(default=0.03, doc="corrugation width for wg2. [um]")
    wg1_width = i3.PositiveNumberProperty(default=0.6,doc="waveguide1 width. [um].")
    wg2_width = i3.PositiveNumberProperty(default=0.4,doc="waveguide2 width. [um].")
    gap = i3.PositiveNumberProperty(default=0.15,doc="gap distance between wg. [um].")
    dutycycle = i3.NonNegativeNumberProperty(default=0.5,doc="ratio of grating vs. spacing in a period. 0 to 1 fraction")
    swg = i3.BoolProperty(default=False,doc = "Enable to remove center fishbone spine.")
    device_layer  = i3.LayerProperty(default=pdk.TECH.PPLAYER.SI, doc="Layer for the device.")
    cladding = i3.BoolProperty(default=True,doc="Boolean to include cladding.")
    cladding_layer = i3.LayerProperty(default=pdk.TECH.PPLAYER.SI_CLADDING, doc="Layer for the device.")
    simulation_geometry = i3.BoolProperty(default=False, doc="Enable to draw geometry for simulation")

    def validate_properties(self):
        if self.dutycycle > 1.0:
            raise i3.PropertyValidationError(
                self,
                f"The current duty cycle value is not valid. Only values between 0 and 1 are accepted.")
        return True

    class Layout(i3.LayoutView):

        def calc_gap_pos(self):
            buswg_ypos = self.wg1_width / 2 + self.dw1 / 2 + self.gap + self.wg2_width / 2 + self.dw2 / 2
            return buswg_ypos

        def _generate_elements(self, elems):
            # Instantiate the bragg waveguides
            Bragg1 = Bragg.BraggStraight()
            Bragg1.dw = self.dw1
            Bragg1.wg_width = self.wg1_width
            Bragg1.period = self.period
            Bragg1.period_num = self.period_num
            Bragg1.cladding = False
            Bragg2 = Bragg.BraggStraight()
            Bragg2.dw = self.dw2
            Bragg2.wg_width = self.wg2_width
            Bragg2.period = self.period
            Bragg2.period_num = self.period_num
            Bragg2.cladding = False
            Bragg2.y_pos = self.calc_gap_pos()
            if self.simulation_geometry:
                Bragg1.simulation_geometry = self.simulation_geometry
                Bragg2.simulation_geometry = self.simulation_geometry

            elems += Bragg1.Layout().elements
            elems += Bragg2.Layout().elements

            if self.cladding:
                if self.simulation_geometry:
                    self.period_num = 5
                elems += i3.Rectangle(  # we can add a cladding layer as well to improve performance
                    layer=self.cladding_layer,
                    center=(self.period*self.period_num/2, self.wg2_width/2+self.dw2/2+self.gap/2),
                    box_size=(self.period*self.period_num, self.wg1_width+self.dw1+self.gap+self.wg2_width+self.dw2+2),
                )
            return elems

        def _generate_ports(self, ports):
            # ORDER IS IMPORTANT - EME smatrix order is based on port order
            # Convention is: left side first, then right side.
            if not self.simulation_geometry:
                ports += i3.OpticalPort(
                    name="Port1", #main wg INPUT
                    position=(0.0, 0.0),
                    angle=180.0,
                )

                ports += i3.OpticalPort(
                    name="Port2", #bus wg INPUT
                    position=(0.0, self.calc_gap_pos()),
                    angle=180.0,
                )

                ports += i3.OpticalPort(
                    name="Port3", #main wg OUTPUT
                    position=((self.period_num * self.period), 0.0),
                    angle=0.0,
                )
                ports += i3.OpticalPort(
                    name="Port4", #bus wg OUTPUT
                    position=((self.period_num * self.period), self.calc_gap_pos()),
                    angle=0.0,
                )

            else:
                ports += i3.OpticalPort(
                    name="Port1",
                    position=(2 * self.period, 0.0),
                    angle=180.0,
                )

                ports += i3.OpticalPort(
                    name="Port2",
                    position=(2 * self.period, self.calc_gap_pos()),
                    angle=180.0,
                )

                ports += i3.OpticalPort(
                    name="Port3",
                    position=((3 * self.period), 0.0),
                    angle=0.0,
                )

                ports += i3.OpticalPort(
                    name="Port4",
                    position=((3 * self.period), self.calc_gap_pos()),
                    angle=0.0,
                )

            return ports

    class CircuitModel(i3.CircuitModelView):
        touchstone_filename = i3.StringProperty(default="CDC_sparam.s4p",
                                                doc="touchstone file, can be from physical simulation or measurement")
        def _generate_model(self):
            smat = i3.circuit_sim.SMatrix1DSweep.from_touchstone(
                self.touchstone_filename,
                term_mode_map = {
                    ('Port1',0): 0, #term name, mode result (index), mapping index
                    ('Port2',0): 1,
                    ('Port3',0): 2,
                    ('Port4',0): 3,
                }
            )
            model = i3.circuit_sim.BSplineSModel.from_smatrix(smat, k=3)
            return model

    class Netlist(i3.NetlistFromLayout):
        pass
if __name__ == "__main__":
    # #Layout
    # dev_cdc = ContraDC()  # init device
    # dev_layout = dev_cdc.Layout()  # create layout
    #
    # dev_layout.visualize(annotate=True) #visualize device in
    # dev_layout.write_gdsii("cdc_layout.gds")  # create gds

    # #Simulation
    # sim_cdc = ContraDC(simulation_geometry=True)
    # sim_layout = sim_cdc.Layout()
    # sim_geom = i3.device_sim.SimulationGeometry(
    #     layout=sim_layout
    # )
    # simulation = i3.device_sim.LumericalEMESimulation(
    #     headless = False,
    #     geometry=sim_geom,
    #     outputs=[
    #         i3.device_sim.MacroOutput(
    #             name='macro_get_sparam',
    #             # filepath must correspond with the file used in the commands.
    #             filepath='CDC_sparam.s4p', #an output file must be provided to use MacroOutput. Since the macro will create an sparam file, we can point to that file
    #             commands=[
    #                 'run;', #run the simulation
    #                 'emepropagate;', #propagate the modes using EME
    #                 'setemeanalysis("wavelength sweep",1);', #enable the wavelength sweep
    #                 'setemeanalysis("start wavelength",1.5e-6);', #start wavelength for sweep
    #                 'setemeanalysis("stop wavelength",1.6e-6);', #stop wavelength for sweep
    #                 'setemeanalysis("number of wavelength points",201);', #number of wavelength points
    #                 'emesweep("wavelength sweep");', #perform the wavelength sweep
    #                 'exportemesweep("CDC_sparam.s4p", "touchstone");' #export the results to a touchstone format
    #                 'exportemesweep("CDC_sparam.dat", "lumerical");' #export the results to a lumerical format
    #             ]
    #         ),
    #     ],
    #     setup_macros=[
    #         i3.device_sim.lumerical_macros.eme_setup(
    #             group_spans=[sim_cdc.period / 2, sim_cdc.period / 2],
    #             cells=[1, 1]
    #         ),
    #         i3.device_sim.Macro(
    #             commands=[
    #                 'select("EME");',
    #                 'set("energy conservation","conserve energy");',
    #                 f'set("y span",{sim_cdc.wg1_width*1e-6 + sim_cdc.gap*1e-6 + sim_cdc.wg2_width * 1e-6 + 1e-6});',
    #                 'set("background material", "Silicon Oxide");',
    #                 'set("start cell group", [1]);',
    #                 'set("end cell group", [2]);',
    #                 'set("periods", [500]);',
    #                 'select("EME::Ports::port_1");',
    #                 f'set("y span",{sim_cdc.wg1_width * 1e-6 + sim_cdc.dw1*1e-6 + sim_cdc.gap * 1e-6});'
    #                 'select("EME::Ports::port_2");',
    #                 f'set("y span",{sim_cdc.wg1_width * 1e-6 + sim_cdc.dw1*1e-6 +sim_cdc.gap * 1e-6});'
    #                 'select("EME::Ports::port_3");',
    #                 f'set("y span",{sim_cdc.wg2_width * 1e-6 + sim_cdc.dw2*1e-6 +sim_cdc.gap * 1e-6});'
    #                 'select("EME::Ports::port_4");',
    #                 f'set("y span",{sim_cdc.wg2_width * 1e-6 + sim_cdc.dw2*1e-6 +sim_cdc.gap * 1e-6});'
    #
    #             ]
    #         ),
    #     ]
    # )
    # simulation.inspect()
    # simulation.get_result("macro_get_sparam"


    # #Transmission S-parameter Simulation
    cdc = ContraDC()
    cdc_cm = cdc.CircuitModel()

    import numpy as np
    wavelengths = np.linspace(1.5, 1.6, 201)
    S = cdc_cm.get_smatrix(wavelengths=wavelengths)
    S.visualize(
        term_pairs=[
            ("Port1", "Port2"),  # Through port
            ("Port1", "Port3"),  # Drop port
        ],
    )