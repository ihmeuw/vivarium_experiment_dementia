import pandas as pd

from vivarium_public_health.disease import ExcessMortalityState


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

        self.pop_view = builder.population.get_view(['cdr'])  # TODO: do I need demog columns here?

    def compute_disability_weight(self, index):
        # get population view including cdr_sb
        # get dw info from the data func
        # determind dws using cdr_sb (make sure you have the right scale, cdr or cdr-sb

        population = self.pop_view.get(index)
        dw_info = self._disability_weight(index)  # this is the data function

        dw = pd.Series(0, index=index)

        mild_index = population.loc[(1.0 <= population['cdr']) & (population['cdr'] < 2.0)]
        dw.loc[mild_index] = dw_info(mild_index)

        moderate_index = population.loc[(2.0 <= population['cdr']) & (population['cdr'] < 3.0)]
        dw.loc[moderate_index] = dw_info(moderate_index)

        severe_index = population.loc[3.0 <= population['cdr']]
        dw.loc[severe_index] = dw.info(severe_index)

        return dw * ((population[self._model] == self.state_id) & (population.alive == 'alive'))


def get_dementia_disability_weight(cause, builder):
    # get sequelae from cause
    # load sequelae disability weights
    # make mild, moderate, severe dataframe

    sequelae = builder.data.load(f'cause.alzheimers_disease_and_other_dementias.sequelae')
    seq_dw = []
    for seq in sequelae:
        df = builder.data.load(f'sequela.{seq}.disability_weight')
        df = df.set_index(list(set(df.columns) - {'value'}))
        df = df.rename(columns={'value': seq.split('_')[0]})
        seq_dw.append(df)
    return pd.concat(seq_dw, axis=1)

