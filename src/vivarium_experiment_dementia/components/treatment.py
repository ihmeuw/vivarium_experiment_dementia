

class ExistingTreatmentAlgorithm:

    configuration_defaults = {
        'dementia_model': {
            'existing_dementia_intervention': {
                'coverage': 0.8,
            }
        }
    }

    @property
    def name(self):
        return 'existing_treatment_algorithm'

    def setup(self, builder):
        self.config = builder.configuration['demential_model']

        self.pop_view = builder.population.get_view(['alzheimers_disease_and_other_dementias', 'treatment_start'])

        builder.event.register_listener('')
        builder.event.register_listener('')

    def on_init_sims(self, event):
        pop = self.pop_view.get(event.index)

        # if has dementia, draw and set treated status

        # otherwise nat


    def on_time_step(self, event):
        pass
        # if current is alz event time, set treatment states


class ExistingTreatmentEffect:

    configuration_defaults = {
        'dementia_model': {
            'existing_dementia_intervention': {
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

