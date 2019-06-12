import pandas as pd
import scipy.stats


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
                'initial_effect_mean': 0.78,  # in terms of cdr_sb for now
                'initial_effect_sd': 0.19,
                'initial_effect_duration': 365,  # days
                'stable_effect_mean': 1.43,
                'stable_effect_sd': 0.46
            }
        }
    }

    @property
    def name(self):
        return 'existing_treatment_effect'

    def setup(self, builder):
        self.config = builder.configuration['dementia_model']

        self.clock = builder.time.clock()

        self.population_view = builder.population.get_view(['treatment_start'])

        self.randomness = {'initial': builder.randomness.get_stream('init_effect_randomness'),
                           'stable': builder.randomness.get_stream('stable_effect_randomness')}

        self.initial_individual_effects = pd.Series()
        self.stable_individual_effect = pd.Series()
        builder.population.initializes_simulants(self.on_initialize_simulants)

        self.initial_duration = pd.Timedelta(days=self.config['existing_dementia_treatment']['initial_effect_duration'])

        builder.value.register_value_modifier('cdr_rate', modifier=self.adjust_cdr_rate)

    def on_initialize_simulants(self, pop_data):

        initial_effect_size = self.get_effect_sizes(pop_data, 'initial')
        self.initial_individual_effects = self.initial_individual_effects.append(initial_effect_size)

        stable_effect_size = self.get_effect_sizes(pop_data, 'stable')
        self.stable_individual_effect = self.stable_individual_effect.append(stable_effect_size)

    def get_effect_sizes(self, pop_data, type: str):
        mean = self.config['existing_dementia_treatment'][f'{type}_effect_mean']
        sd = self.config['existing_dementia_treatment'][f'{type}_effect_sd']

        draw = self.randomness[type].get_draw(pop_data.index)
        effect_size = scipy.stats.norm(mean, sd).ppf(draw)
        effect_size[effect_size < 0] = 0.0
        effect_size = effect_size / 6.0  # TODO: convert to CDR. temporary
        return pd.Series(effect_size, index=pop_data.index)

    def adjust_cdr_rate(self, index, exposure):
        pop = self.population_view.get(index)

        # cdr rate is completely determined by treatment start date.
        within_initial_index = pop.loc[(self.clock() - pop['treatment_start'] <= self.initial_duration)].index
        stable_index = pop.loc[(self.clock() - pop['treatment_start'] > self.initial_duration)].index

        exposure.loc[within_initial_index] = self.initial_individual_effects.loc[within_initial_index]
        exposure.loc[stable_index] = self.stable_individual_effect.loc[stable_index]
