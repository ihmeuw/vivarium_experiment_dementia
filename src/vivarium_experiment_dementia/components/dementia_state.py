import pandas as pd

from vivarium_public_health.disease import ExcessMortalityState


class DementiaExcessMortalityState(ExcessMortalityState):

    def __init__(self):
        self.cause = 'alzheimers_and_other_dementias'
        super().__init__(self.cause)
        self._get_data_functions['disability_weight'] = get_dementia_disability_weight

    @property
    def name(self):
        return "dementia_state"

    def setup(self, builder):
        super().setup(builder)
        self.cdr_sb = builder.value.get_value('cdr_sb')

    def compute_disability_weight(self, index):
        population = self.population_view.get(index)
        dw_info = self._disability_weight(population.index)  # this is the data function
        cdr_sb = self.cdr_sb(index)

        dw = pd.Series(0, index=index)

        # subset and assign dw based on cdr sb levels
        # mild_index =
        # moderate_index
        # severe_index
        #
        # dw.loc[(1. <= dw['cdr_sb'] & dw['cdr_sb'] < 2.), 'mild']
        # dw.loc[(1. <= dw['cdr_sb'] & dw['cdr_sb'] < 2.), 'moderate']
        # dw.loc[(1. <= dw['cdr_sb'] & dw['cdr_sb'] < 2.), 'severe']

        # return the pandas series

        # determine severity from cdr-sb
        # self._disability_weight(population.index) * ((population[self._model] == self.state_id)
        #                                                     & (population.alive == 'alive'))


def get_dementia_disability_weight(builder):
    # get sequelae from cause
    # load sequelae disability weights
    # make mild, moderate, severe dataframe

    sequelae = builder.data.load(f'alzheimers_and_other_dementias.sequelae')
    seq_dw = []
    for seq in sequelae:
        seq_dw.append(builder.data.load())

    return pd.concat(seq_dw)
