from vivarium_public_health.disease import SusceptibleState, DiseaseModel
from vivarium_experiment_dementia.components import DementiaExcessMortalityState


class Dementia_SI:

    def __init__(self):
        super().__init__()
        self.cause = 'alzheimers_disease_and_other_dementias'

    @property
    def name(self):
        return 'dementia_SI'

    def setup(self, builder):

        healthy = SusceptibleState(self.cause)
        infected = DementiaExcessMortalityState()

        healthy.allow_self_transitions()
        healthy.add_transition(infected, source_data_type='rate')
        infected.allow_self_transitions()

        builder.components.add_components([DiseaseModel(self.cause, states=[healthy, infected])])

    def __repr__(self):
        return 'dementia_SI()'
