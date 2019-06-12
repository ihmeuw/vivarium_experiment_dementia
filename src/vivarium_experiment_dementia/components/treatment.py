import pandas as pd


class ExistingTreatmentAlgorithm:

    configuration_defaults = {
        'dementia_model': {
            'existing_dementia_treatment': {
                'coverage': 0.8,
            }
        }
    }

    @property
    def name(self):
        return 'existing_treatment_algorithm'

    def setup(self, builder):
        self.config = builder.configuration['dementia_model']

        self.clock = builder.time.clock()

        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=['treatment_start'],
                                                 requires_columns=['alzheimers_disease_and_other_dementias'])

        self.pop_view = builder.population.get_view(['alzheimers_disease_and_other_dementias', 'treatment_start',
                                                     'alzheimers_disease_and_other_dementias_event_time'])
        self.pop_subview = self.pop_view.subview(['alzheimers_disease_and_other_dementias'])

        self.init_randomness = builder.randomness.get_stream('assign_treated_initially')
        self.time_step_randomness = builder.randomness.get_stream('assign_treated_ts')

        builder.event.register_listener('time_step', self.on_time_step)

    def on_initialize_simulants(self, pop_data):
        pop = self.pop_subview.get(pop_data.index)

        pop['treatment_start'] = pd.NaT

        dementia_index = pop.loc[(pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias')].index
        treated_index = self.init_randomness.filter_for_probability(dementia_index,
                                                                    self.config['existing_dementia_treatment']['coverage'])

        pop.loc[treated_index, 'treatment_start'] = self.clock()

        self.pop_view.update(pop)

    def on_time_step(self, event):
        pop = self.pop_view.get(event.index)

        dementia_index = pop.loc[pop['alzheimers_disease_and_other_dementias_event_time'] == self.clock()].index
        treated_index = self.time_step_randomness.filter_for_probability(dementia_index,
                                                                         self.config['existing_dementia_treatment']['coverage'])

        pop.loc[treated_index, 'treatment_start'] = event.time

        self.pop_view.update(pop)


class ExistingTreatmentEffect:

    configuration_defaults = {
        'dementia_model': {
            'existing_dementia_treatment': {
                'initial_effect_mean': 1.0,
                'initial_effect_sd': 1.0,
                'initial_effect_duration': 365,  # days
                'stable_effect_mean': 1.0,
                'stable_effect_sd': 1.0
            }
        }
    }

    @property
    def name(self):
        return 'existing_treatment_effect'

    def setup(self, builder):
        pass

    # TODO: register value modifier that is
