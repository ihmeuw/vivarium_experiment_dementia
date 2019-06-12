import pandas as pd


class DementiaProgression:

    configuration_defaults = {
        'dementia_model': {
            'cdr_rate': 0.406667  # annual increase. corresponds to cdr_sb of 2.44
        }
    }

    @property
    def name(self):
        return 'cdr'

    def setup(self, builder):
        self.config = builder.configuration['dementia_model']

        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=['cdr'],
                                                 requires_columns=['alzheimers_disease_and_other_dementias'])

        # register cdr_rate value producer to give a hook for treatment to reach in with
        self.cdr_rate = builder.value.register_rate_producer('cdr_rate', self._cdr_rate)

        self.randomness_initial_cases = builder.randomness.get_stream('initial_cases')
        self.randomness_cdr_noise = builder.randomness.get_stream('cdr_noise')

        seq_prevalence = self.get_sequelae_prevalence(builder)
        self.sequelae_prevalance = builder.lookup.build_table(seq_prevalence)

        self.pop_view = builder.population.get_view(['alive', 'alzheimers_disease_and_other_dementias', 'alzheimers_disease_and_other_dementias_event_time', 'cdr'])
        self.pop_subview = self.pop_view.subview(['alzheimers_disease_and_other_dementias'])

        self.clock = builder.time.clock()

        builder.event.register_listener('time_step', self.on_time_step)

    def get_sequelae_prevalence(self, builder):
        sequelae = builder.data.load('cause.alzheimers_disease_and_other_dementias.sequelae')
        prevalence = []
        for seq in sequelae:
            df = builder.data.load(f'sequela.{seq}.prevalence')
            df = df.set_index(list(set(df.columns) - {'value'}))
            df = df.rename(columns={'value': seq.split('_')[0]})  # TODO: break this out later
            prevalence.append(df)

        return pd.concat(prevalence, axis=1).reset_index()

    def on_initialize_simulants(self, pop_data):
        pop = self.pop_subview.get(pop_data.index)
        pop['cdr'] = 0.0

        dementia_index = pop.loc[(pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias')].index

        # prevalence of the sequelae, normalized
        seq_prevalence = self.sequelae_prevalance(dementia_index)
        seq_prevalence = seq_prevalence.divide(seq_prevalence.sum(axis=1), axis=0)

        # choose mild, moderate or severe and remap to starting value. Prevalent dementia cases
        # at the beginning are relatively few so this is subject to noise
        dementia_cdr = self.randomness_initial_cases.choice(dementia_index, seq_prevalence.columns, seq_prevalence)
        dementia_cdr = dementia_cdr.replace({'mild': 1.0, 'moderate': 2.0, 'severe': 3.0})

        # add uniform noise
        dementia_cdr += self.randomness_cdr_noise.get_draw(dementia_index)

        # put back in
        pop.loc[dementia_index, 'cdr'] = dementia_cdr
        self.pop_view.update(pop)

    def on_time_step(self, event):
        pop = self.pop_view.get(event.index)
        pop = pop.loc[pop['alive'] == 'alive']  # only progress people who are alive

        # tick people forward, cdr_rate is zero if they don't have alzheimers
        pop['cdr'] += self.cdr_rate(event.index)  # TODO: what is the rescale_post_processor doing? is this correct?

        # init inicident cases cdr to 1.0
        pop.loc[(pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias') & (pop['alzheimers_disease_and_other_dementias_event_time'] == self.clock()), 'cdr'] = 1.0

        self.pop_view.update(pop)

    def _cdr_rate(self, index):
        # zero if don't have, otherwise default. The treatment component will modify this as needed
        pop = self.pop_view.get(index)

        cdr_rate = pd.Series(0.0, index=index)
        with_disease = pop.loc[pop['alzheimers_disease_and_other_dementias'] == 'alzheimers_disease_and_other_dementias'].index
        cdr_rate.loc[with_disease] = self.config['cdr_rate']

        return cdr_rate
