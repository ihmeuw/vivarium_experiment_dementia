import pandas as pd

from vivarium_public_health.disease import ExcessMortalityState, SusceptibleState, DiseaseModel


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


class DementiaExcessMortalityState(ExcessMortalityState):

    def __init__(self):
        self.cause = 'alzheimers_disease_and_other_dementias'
        super().__init__(self.cause)
        self._get_data_functions['disability_weight'] = get_dementia_disability_weight

    @property
    def name(self):
        return "dementia_state"

    def setup(self, builder):
        super().setup(builder)

        self.pop_view = builder.population.get_view(['alive', 'cdr'])

    def compute_disability_weight(self, index):
        # get population view including cdr
        # get dw info from the data func
        # determine dw using cdr_sb

        population = self.pop_view.get(index)
        dw_info = self._disability_weight(index)  # this is the get data function

        dw = pd.Series(0, index=index)

        mild_index = (1.0 <= population['cdr']) & (population['cdr'] < 2.0)
        dw.loc[mild_index] = dw_info.loc[mild_index, 'mild']

        moderate_index = (2.0 <= population['cdr']) & (population['cdr'] < 3.0)
        dw.loc[moderate_index] = dw_info.loc[moderate_index, 'moderate']

        severe_index = (3.0 <= population['cdr'])
        dw.loc[severe_index] = dw_info.loc[severe_index, 'severe']

        return dw * (population.alive == 'alive')


def get_dementia_disability_weight(cause, builder):
    sequelae = builder.data.load(f'cause.alzheimers_disease_and_other_dementias.sequelae')
    seq_dw = []
    for seq in sequelae:
        df = builder.data.load(f'sequela.{seq}.disability_weight')
        df = df.set_index(list(set(df.columns) - {'value'}))
        df = df.rename(columns={'value': seq.split('_')[0]})  # sequelae start with mild_, moderate_, severe_
        seq_dw.append(df)

    return pd.concat(seq_dw, axis=1).reset_index()
