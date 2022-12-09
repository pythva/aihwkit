# creating rpu structure with PCM devices as processer


class PCMLikeNoiseModel(BaseNoiseModel):

    def __init__(
            self,
            prog_coeff: Optional[List[float]] = None,
            g_converter: Optional[BaseConductanceConverter] = None,
            g_max: Optional[float] = None, # maximum voltage
            t_read: float = 250.0e-9, # the time unit for update
            #Low-frequency noise could be particularly detrimental to long-term inference performance. 
            #While 1/f γ noise ( γ = 0.9 to 1.1) and Random Telegraph Noise have been observed in PCM, 
            #for the modeling we assume an ideal 1/f behavior
            t_0: float = 20.0,
            prog_noise_scale: float = 1.0,
            read_noise_scale: float = 1.0,
            drift_scale: float = 1.0,# drifting parameter
            #The conductance of the PCM is observed to decrease over time which 
            #is typically attributed to structural relaxation of the phase conﬁguration 
            #formed as a result of each programming event
            
    ):
# the default parameter for the PCM like model




def create_rpu_config():

    from aihwkit.simulator.configs import InferenceRPUConfig
    from aihwkit.simulator.configs.utils import BoundManagementType, WeightNoiseType
    from aihwkit.inference import PCMLikeNoiseModel

    # this line of codes allows the The Tiki-taka learning rule
    unit_cell_devices=[
            SoftBoundsDevice(w_min=-0.3, w_max=0.3),
            SoftBoundsDevice(w_min=-0.6, w_max=0.6)
        ],

    rpu_config = InferenceRPUConfig()
    rpu_config.backward.bound_management = BoundManagementType.NONE
    rpu_config.forward.out_res = -1.  # Turn off (output) ADC discretization.
    rpu_config.forward.w_noise_type = WeightNoiseType.ADDITIVE_CONSTANT
    rpu_config.forward.w_noise = 0.02
    rpu_config.noise_model = PCMLikeNoiseModel(g_max=25.0)# the parameter can be modified according to the desire value

    return rpu_config

rpu_config.noise_model = PCMLikeNoiseModel(g_max=25.0)



'''
weight_scaling_omega controls what is teh range of the values (conductances) that can be programmed on the analog chip. 
For example, 1 means that the max weight will be mapped to gmax. 
so it is how you map the neural network weights to the conductance Gmax and Gmin values
in case of .4 the wmax will be set to 0.4*gmax which is not ideal
'''

# the definition of a ideal device 

class IdealDevice(_PrintableMixin):
    """Ideal update behavior (using floating point), but forward/backward
    might be non-ideal.
    Ideal update behavior (using floating point), however,
    forward/backward might still have a non-ideal ADC or noise added.
    """

    bindings_class: ClassVar[Type] = devices.IdealResistiveDeviceParameter

    construction_seed: int = 0
    """If not ``0``, set a unique seed for hidden parameters during
    construction."""

    diffusion: float = 0.0
    """Standard deviation of diffusion process."""

    lifetime: float = 0.0
    r"""One over `decay_rate`, ie :math:`1/r_\text{decay}`."""

    def as_bindings(self) -> devices.IdealResistiveDeviceParameter:
        """Return a representation of this instance as a simulator bindings object."""
        return parameters_to_bindings(self)

    def requires_diffusion(self) -> bool:
        """Return whether device has diffusion enabled."""
        return self.diffusion > 0.0

    def requires_decay(self) -> bool:
        """Return whether device has decay enabled."""
        return self.lifetime > 0.0
