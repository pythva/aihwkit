

from torch import Tensor
from aihwkit.nn import AnalogLinear

model = AnalogLinear(2, 2)
model(Tensor([[0.1, 0.2], [0.3, 0.4]]))

"""## RPU Configuration
Now that the package is installed and running, we can start working on creating the LeNet5 network.

AIHWKIT offers different Analog layers that can be used to build a network, including AnalogLinear 
and AnalogConv2d which will be the main layers used to build the present network. 
"""

def create_rpu_config_1():

    from aihwkit.simulator.configs import SingleRPUConfig
    from aihwkit.simulator.configs.devices import ConstantStepDevice

    rpu_config=SingleRPUConfig(device=ConstantStepDevice())

    return rpu_config


def create_rpu_config_2():

    from aihwkit.simulator.presets import ReRamSBPreset

    rpu_config=ReRamSBPreset()

    return rpu_config

# the PCM style for configeration 

def create_rpu_config_PCM():

    from aihwkit.simulator.configs import InferenceRPUConfig
    from aihwkit.simulator.configs.utils import BoundManagementType, WeightNoiseType
    from aihwkit.inference import PCMLikeNoiseModel

    rpu_config = InferenceRPUConfig()
    rpu_config.backward.bound_management = BoundManagementType.NONE
    rpu_config.forward.out_res = -1.  # Turn off (output) ADC discretization.
    rpu_config.forward.w_noise_type = WeightNoiseType.ADDITIVE_CONSTANT
    rpu_config.forward.w_noise = 0.02
    rpu_config.noise_model = PCMLikeNoiseModel(g_max=25.0)

    return rpu_config

"""We can now use the defined rpu_config as input of the network model:"""

from torch.nn import Tanh, MaxPool2d, LogSoftmax, Flatten
from aihwkit.nn import AnalogConv2d, AnalogLinear, AnalogSequential

def create_analog_network(rpu_config):
    
    channel = [16, 32, 512, 128]
    model = AnalogSequential(
        AnalogConv2d(in_channels=1, out_channels=channel[0], kernel_size=5, stride=1,
                        rpu_config=rpu_config),
        Tanh(),
        MaxPool2d(kernel_size=2),
        AnalogConv2d(in_channels=channel[0], out_channels=channel[1], kernel_size=5, stride=1,
                        rpu_config=rpu_config),
        Tanh(),
        MaxPool2d(kernel_size=2),
        Tanh(),
        Flatten(),
        AnalogLinear(in_features=channel[2], out_features=channel[3], rpu_config=rpu_config),
        Tanh(),
        AnalogLinear(in_features=channel[3], out_features=10, rpu_config=rpu_config),
        LogSoftmax(dim=1)
    )

    return model

"""## Analog Optimizer 

We will use the cross entropy criteria to calculate the loss and the Stochastic Gradient Descent (SGD) as optimizer:
"""

from torch.nn import CrossEntropyLoss

criterion = CrossEntropyLoss()


from aihwkit.optim import AnalogSGD

def create_analog_optimizer(model):
    """Create the analog-aware optimizer.
    Args:
        model (nn.Module): model to be trained

    Returns:
        Optimizer: created analog optimizer
    """
    optimizer = AnalogSGD(model.parameters(), lr=0.01) # we will use a learning rate of 0.01 as in the paper
    optimizer.regroup_param_groups(model)

    return optimizer
