from rl_coach.agents.clipped_ppo_agent import ClippedPPOAgentParameters
from rl_coach.base_parameters import VisualizationParameters, PresetValidationParameters
from rl_coach.core_types import TrainingSteps, EnvironmentEpisodes, EnvironmentSteps, RunPhase
from rl_coach.environments.gym_environment import GymVectorEnvironment
from rl_coach.graph_managers.basic_rl_graph_manager import BasicRLGraphManager
from rl_coach.graph_managers.graph_manager import ScheduleParameters
from rl_coach.schedules import LinearSchedule

from rl_coach.exploration_policies.categorical import CategoricalParameters
from rl_coach.filters.filter import NoInputFilter, NoOutputFilter, InputFilter
from rl_coach.filters.observation.observation_stacking_filter import ObservationStackingFilter
from rl_coach.filters.observation.observation_rgb_to_y_filter import ObservationRGBToYFilter
from rl_coach.filters.observation.observation_to_uint8_filter import ObservationToUInt8Filter
from rl_coach.memories.memory import MemoryGranularity

####################
# Graph Scheduling #
####################

schedule_params = ScheduleParameters()
schedule_params.improve_steps = TrainingSteps(10000000)
schedule_params.steps_between_evaluation_periods = EnvironmentEpisodes(60)
schedule_params.evaluation_steps = EnvironmentEpisodes(5)
schedule_params.heatup_steps = EnvironmentSteps(1)

#########
# Agent #
#########
agent_params = ClippedPPOAgentParameters()

agent_params.memory.max_size = (MemoryGranularity.Transitions, 10**5)

agent_params.network_wrappers['main'].learning_rate = 0.0006
agent_params.network_wrappers['main'].input_embedders_parameters['observation'].activation_function = 'relu'
agent_params.network_wrappers['main'].middleware_parameters.activation_function = 'relu'
agent_params.network_wrappers['main'].batch_size = 64
agent_params.network_wrappers['main'].optimizer_epsilon = 1e-5
agent_params.network_wrappers['main'].adam_optimizer_beta2 = 0.999

agent_params.algorithm.clip_likelihood_ratio_using_epsilon = 0.2
agent_params.algorithm.clipping_decay_schedule = LinearSchedule(1.0, 0, 1000000)
agent_params.algorithm.beta_entropy = 0.01  # also try 0.001
agent_params.algorithm.gae_lambda = 0.95
agent_params.algorithm.discount = 0.9
agent_params.algorithm.optimization_epochs = 7
agent_params.algorithm.estimate_state_value_using_gae = True
agent_params.algorithm.num_steps_between_copying_online_weights_to_target = EnvironmentEpisodes(30)
agent_params.algorithm.num_consecutive_playing_steps = EnvironmentEpisodes(30)
agent_params.exploration = CategoricalParameters()

###############
# Environment #
###############
DeepRacerInputFilter = InputFilter(is_a_reference_filter=True)
DeepRacerInputFilter.add_observation_filter('observation', 'to_grayscale', ObservationRGBToYFilter())
DeepRacerInputFilter.add_observation_filter('observation', 'to_uint8', ObservationToUInt8Filter(0, 255))
DeepRacerInputFilter.add_observation_filter('observation', 'stacking', ObservationStackingFilter(1))

env_params = GymVectorEnvironment()
env_params.default_input_filter = DeepRacerInputFilter
env_params.level = 'SageMaker-DeepRacer-Discrete-v0'

vis_params = VisualizationParameters()
vis_params.dump_mp4 = False

########
# Test #
########
preset_validation_params = PresetValidationParameters()
preset_validation_params.test = True
preset_validation_params.min_reward_threshold = 4000
preset_validation_params.max_episodes_to_achieve_reward = 20

graph_manager = BasicRLGraphManager(agent_params=agent_params, env_params=env_params,
                                    schedule_params=schedule_params, vis_params=vis_params,
                                    preset_validation_params=preset_validation_params)
