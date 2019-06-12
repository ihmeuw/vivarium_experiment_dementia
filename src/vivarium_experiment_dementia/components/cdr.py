import pandas as pd

# TODO: don't waffle between cdr_sb and cdr. pick one


class DementiaProgression:

    configuration_defaults = {
        'dementia_model': {
            'cdr_sb_rate': 2.44  # annual
        }
    }

    @property
    def name(self):
        return 'cdr'

    def setup(self, builder):
        self.config = builder.configuration['dementia_model']

        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=['cdr'],
                                                 requires_columns=['alzheimers_disease_and_other_dementias'])

        # register cdr_sb_rate value producer to give a hook for treatment to reach in with
        self.cdr_rate = builder.value.register_rate_producer('cdr_rate', self._cdr_rate)

        self.pop_view = builder.population.get_view(['alzheimers_and_other_dementias', 'cdr'])
        self.pop_subview = self.pop_view.get_subview(['alzheimers_and_other_dementias'])

        self.clock = builder.time.clock()

        builder.event.register_listener('time_step', self.on_time_step)

    # TODO: Not everyone starts right at the beginning. Use prevalence or something to mix people around
    def on_initialize_simulants(self, pop_data):
        pop = self.pop_subview.get(pop_data.index)

        pop['cdr'] = 0.0
        pop.loc[pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias', 'cdr'] = 1.0

        self.pop_subview.update(pop)

    def on_time_step(self, event):
        pop = self.pop_view.get(event.index)
        pop['cdr'] += self.cdr_rate(event.index)  # TODO: what is the rescale_post_processor doing? is this correct?

        self.pop_view.update(pop)

    def _cdr_rate(self, index):
        # zero if don't have, otherwise default.
        # the treatment component will modify this as needed
        pop = self.pop_view.get(index)

        cdr_rate = pd.Series(0.0, index=index)
        with_disease = pop.loc[pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias'].index
        cdr_rate.loc[with_disease] = self.config['cdr_sb_rate'] / 6.0

        return cdr_rate
