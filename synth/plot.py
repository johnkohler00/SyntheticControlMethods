# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

import numpy as np

class Plot(object):

    def plot(self, panels, figsize=(15, 12), 
            treated_label="Treated Unit",
            synth_label="Synthetic Control"):

        #Extract Synthetic Control
        synth = self.synth_outcome
        time = self.dataset[self.time].unique()

        plt = self._get_plotter()
        fig = plt.figure(figsize=figsize)
        valid_panels = ['original', 'pointwise', 'cumulative', 'in-space placebo']
        for panel in panels:
            if panel not in valid_panels:
                raise ValueError(
                    '"{}" is not a valid panel. Valid panels are: {}.'.format(
                        panel, ', '.join(['"{}"'.format(e) for e in valid_panels])
                    )
                )
        
        n_panels = len(panels)
        ax = plt.subplot(n_panels, 1, 1)
        idx = 1

        if 'original' in panels:
            ax.set_title("{} vs. {}".format(treated_label, synth_label))
            ax.plot(time, synth.T, 'r--', label=synth_label)
            ax.plot(time ,self.treated_outcome_all, 'b-', label=treated_label)
            ax.axvline(self.treatment_period-1, linestyle=':', color="gray")
            ax.annotate('Treatment', 
                xy=(self.treatment_period-1, self.treated_outcome[-1]*1.2),
                xytext=(-80, -4),
                xycoords='data',
                #textcoords="data",
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
            ax.set_ylabel(self.outcome_var)
            ax.set_xlabel(self.time)
            ax.legend()
            if idx != n_panels:
                plt.setp(ax.get_xticklabels(), visible=False)
            idx += 1

        if 'pointwise' in panels:

            ax = plt.subplot(n_panels, 1, idx, sharex=ax)
            #Subtract outcome of synth from both synth and treated outcome
            normalized_treated_outcome = self.treated_outcome_all - synth.T
            normalized_synth = np.zeros(self.periods_all)
            most_extreme_value = np.max(np.absolute(normalized_treated_outcome))

            ax.set_title("Pointwise Effects")
            ax.plot(time, normalized_synth, 'r--', label=synth_label)
            ax.plot(time ,normalized_treated_outcome, 'b-', label=treated_label)
            ax.axvline(self.treatment_period-1, linestyle=':', color="gray")
            ax.set_ylim(-1.1*most_extreme_value, 1.1*most_extreme_value)
            ax.annotate('Treatment', 
                xy=(self.treatment_period-1, 0.5*most_extreme_value),
                xycoords='data',
                xytext=(-80, -4),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
            ax.set_ylabel(self.outcome_var)
            ax.set_xlabel(self.time)
            ax.legend()
            if idx != n_panels:
                plt.setp(ax.get_xticklabels(), visible=False)
            idx += 1

        if 'cumulative' in panels:
            ax = plt.subplot(n_panels, 1, idx, sharex=ax)
            #Compute cumulative treatment effect as cumulative sum of pointwise effects
            cumulative_effect = np.cumsum(normalized_treated_outcome[self.periods_pre_treatment:])
            cummulative_treated_outcome = np.concatenate((np.zeros(self.periods_pre_treatment), cumulative_effect), axis=None)
            normalized_synth = np.zeros(self.periods_all)

            ax.set_title("Cumulative Effects")
            ax.plot(time, normalized_synth, 'r--', label=synth_label)
            ax.plot(time ,cummulative_treated_outcome, 'b-', label=treated_label)
            ax.axvline(self.treatment_period-1, linestyle=':', color="gray")
            #ax.set_ylim(-1.1*most_extreme_value, 1.1*most_extreme_value)
            ax.annotate('Treatment', 
                xy=(self.treatment_period-1, cummulative_treated_outcome[-1]*0.3),
                xycoords='data',
                xytext=(-80, -4),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
            ax.set_ylabel(self.outcome_var)
            ax.set_xlabel(self.time)
            ax.legend()
            if idx != n_panels:
                plt.setp(ax.get_xticklabels(), visible=False)
            idx += 1

        if 'in-space placebo' in panels:
            assert self.in_space_placebos != None, "Must run in_space_placebo() before you can plot!"
            
            ax = plt.subplot(n_panels, 1, idx, sharex=ax)
            zero_line = np.zeros(self.periods_all)
            normalized_treated_outcome = self.treated_outcome_all - synth.T
            
            ax.set_title("In-space placebo's")
            ax.plot(time, zero_line, 'k--')

            #Plot each placebo
            for i in range(self.n_controls):

                #Normalize the placebo wrt to the unit it simulates
                # ((len(unit_list)-1) x treatment_period)
                normalized_placebo = (self.in_space_placebos[i] - self.control_outcome_all[:, i].T).T
                ax.plot(time, normalized_placebo, ('0.7'))

            ax.axvline(self.treatment_period-1, linestyle=':', color="gray")
            ax.plot(time, normalized_treated_outcome, 'b-', label=treated_label)

            #ax.set_ylim(-1.1*most_extreme_value, 1.1*most_extreme_value)
            '''
            ax.annotate('Treatment',
                xy=(self.treatment_period-1, cummulative_treated_outcome[-1]*0.3),
                xycoords='data',
                xytext=(-80, -4),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
            '''
            ax.set_ylabel(self.outcome_var)
            ax.set_xlabel(self.time)
            ax.legend()
            if idx != n_panels:
                plt.setp(ax.get_xticklabels(), visible=False)
            idx += 1

        fig.tight_layout(pad=3.0)
        plt.show()

    def _get_plotter(self):  # pragma: no cover
        """Some environments do not have matplotlib. Importing the library through
        this method prevents import exceptions.

        Returns:
          plotter: `matplotlib.pyplot
        """
        import matplotlib.pyplot as plt
        return plt