from si_fab import all as pdk
from ipkiss3 import all as i3

class BraggStraight(i3.PCell):  # we define a component using i3.PCell
    """Bragg Grating with 1 input and 1 output."""  # a short description of the class is always useful to include
    _name_prefix = "BraggStraight"
    trace_template = i3.TraceTemplateProperty(doc="Trace template of the access waveguide.") #template for the waveguide
    # Parameters
    period = i3.PositiveNumberProperty(default=0.32,doc="distance between a set of gratings. [um]")
    period_num = i3.PositiveIntProperty(default=100,doc="amount of periods.")
    dw = i3.NonNegativeNumberProperty(default=0.04,doc="corrugation width. [um]")
    dutycycle = i3.NonNegativeNumberProperty(default=0.5,doc="ratio of grating vs. spacing in a period. 0 to 1 fraction")
    wg_width = i3.PositiveNumberProperty(default=0.5,doc="waveguide width. [um].")
    swg = i3.BoolProperty(default=False,doc = "Enable to remove center fishbone spine.")
    device_layer  = i3.LayerProperty(default=pdk.TECH.PPLAYER.SI, doc="Layer for the device.")
    cladding = i3.BoolProperty(default=True,doc="Boolean to include cladding.")
    cladding_layer = i3.LayerProperty(default=pdk.TECH.PPLAYER.SI_CLADDING, doc="Layer for the device.")
    simulation_geometry = i3.BoolProperty(default=False, doc="Enable to draw geometry for simulation")
    x_pos = i3.NumberProperty(default=0.0, doc="device position x")
    y_pos = i3.NumberProperty(default=0.0, doc="device position y")

    def _default_trace_template(self):  # this trace template is defined in the PDK
        return pdk.SiWireWaveguideTemplate()

    def validate_properties(self):
        if self.dutycycle > 1.0:
            raise i3.PropertyValidationError(
                self,
                f"The current duty cycle value is not valid. Only values between 0 and 1 are accepted.")
        return True

    class Layout(i3.LayoutView):

        def _generate_elements(self, elems):
            if self.simulation_geometry:
                self.period_num = 5
            for i in range(0,self.period_num):
                elems += i3.Rectangle(
                    layer = self.device_layer,
                    center = (self.x_pos + self.period*self.dutycycle/2 + (i*self.period), self.y_pos),
                    box_size = (self.period*self.dutycycle, self.wg_width+self.dw),
                )
            if not self.swg:
                elems += i3.Rectangle(
                    layer = self.device_layer,
                    center = (self.x_pos + self.period*self.period_num/2 , self.y_pos),
                    box_size = (self.period*self.period_num,self.wg_width-self.dw)
                )

            if self.cladding:
                elems += i3.Rectangle(
                    layer=self.cladding_layer,
                    center=(self.period*self.period_num/2, 0.0),
                    box_size=(self.period*self.period_num, self.wg_width+self.dw*2+2),
                )
            return elems

        def _generate_ports(self, ports):
            trace_template = self.trace_template
            if not self.simulation_geometry:
                ports += i3.OpticalPort(  # you can also add electrical ports in the same way
                    name="in1",  # this is the port name you will see when this PCell is used
                    position=(self.x_pos, self.y_pos),  # position is coincident with the relevant element
                    angle=180.0,  # angle with respect to the x-axis, always facing outwards from the port
                    trace_template=trace_template,  # the trace template for the optical port
                )
                ports += i3.OpticalPort(
                    name="out1",
                    position=((self.x_pos + self.period_num * self.period), self.y_pos),
                    angle=0.0,
                    trace_template=trace_template,
                )

            else:
                ports += i3.OpticalPort(  # you can also add electrical ports in the same way
                    name="in1",  # this is the port name you will see when this PCell is used
                    position=(self.period * 2, 0.0),  # position is coincident with the relevant element
                    angle=180.0,  # angle with respect to the x-axis, always facing outwards from the port
                    trace_template=trace_template,  # the trace template for the optical port
                )
                ports += i3.OpticalPort(
                    name="out1",
                    position=(self.period*3, 0),
                    angle=0.0,
                    trace_template=trace_template,
                )

            return ports

    class Netlist(i3.NetlistFromLayout):
        pass

if __name__ == "__main__":
    dev_bragg = BraggStraight() #init device
    dev_layout = dev_bragg.Layout() #create layout

    #dev_layout.visualize(annotate=True) #visualize device in python
    dev_layout.write_gdsii("bragg_layout.gds") #create gds
    #dev_layout.visualize_2d(process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL) #top view with material info

    #visualize cross section
    # bragg_layout.cross_section(
    #      cross_section_path=i3.Shape([(0, -1.5), (0, 1.5)]),
    #      process_flow=pdk.TECH.VFABRICATION.PROCESS_FLOW_FEOL,
    #  ).visualize()

    #Create Simulation
    # sim_bragg = BraggStraight(simulation_geometry=True)
    # sim_layout = sim_bragg.Layout()
    # sim_geom = i3.device_sim.SimulationGeometry(
    #     layout = sim_layout
    # )
    # simulation = i3.device_sim.LumericalEMESimulation(
    #     geometry=sim_geom,
    #     outputs=[
    #         i3.device_sim.SMatrixOutput(
    #             name='smatrix',
    #             wavelength_range=(1.5, 1.6, 100)
    #        )
    #     ],
    #     setup_macros=[
    #         i3.device_sim.lumerical_macros.eme_setup(
    #             group_spans=[sim_bragg.period/2, sim_bragg.period/2],
    #             cells=[1, 1]
    #         ),
    #         i3.device_sim.Macro(
    #         commands=[
    #             'select("EME");',
    #             'set("energy conservation","conserve energy");',
    #             f'set("y span",{sim_bragg.wg_width*1e-6 + 1e-6});',
    #             'set("background material", "Silicon Oxide");',
    #             'set("start cell group", [1]);',
    #             'set("end cell group", [2]);',
    #             'set("periods", [500]);',
    #             ]
    #         ),
    #     ]
    # )
    # simulation.inspect()
