'''
Created on Jun 21, 2016

@author: jivan
Takes any number of instantiated predictors as initialization arguments
and uses them to generate a consensus prediction
by totaling the confidence values given by each predictor.
'''
from __future__ import print_function
from _collections import defaultdict
import operator
import logging
from numpy import median


logger = logging.getLogger(__name__)


class ConsensusPredictor(object):
    # All scores given to failed and successful predictions as returned from .predict()
    #    during training.
    fail_scores = []
    success_scores = []

    # If __init__() kwarg 'log_contributions' is True, This contains information
    #    about which predictors contributed how much score to each failure and success.
    # The format is { <rs_id>: { <predictor>: {<charname>: {<tone>: <score_contributed>} } } }
    contributions = None

    def __init__(
        self, predictors, training_data, log_contributions=False, helpfulness_cutoff=0.0001):
        ''' *predictors* is a list of single-characteristic predictor instances
                (currently BandPredictor, SKLearnPredictor)
            *training_data* is a dictionary of the form: {(id, tone): {charname: charvalue}}
            *log_contributions* turns on additional record-keeping for insight into
                which predictors are helping (or potentially harming) predictions.
            *drop_unhelpful*: A flag to indicate if basic predictors with a helpfulness
                < helpfulness_cutoff should be eliminated from the predictor set used by
                this predictor.
            *helpfulness_cutoff*: The minimum helpfulness value to consider if *drop_unhelpful*
                is True.
        '''
        logger.info('--- Initializing ConsensusPredictor (python id: {})'.format(id(self)))
        self.helpfulness_cutoff = helpfulness_cutoff
        self.accuracy_cutoff = 0.2  # Value expected from random guessing w/ 5 tones
        if log_contributions:
            self.contributions = _get_contribution_data_structure()

        self._predictors = list(predictors)
        self._train(training_data, helpfulness_cutoff=helpfulness_cutoff)
#         if drop_unhelpful:
#             helpful_predictors = []
#             for p in self._predictors:
#                 p_helpfulness = self.helpfulness_by_predictor_charname[(p.name, p.charname)]
#                 if p_helpfulness >= helpfulness_cutoff:
#                     helpful_predictors.append(p)
#                 else:
#                     msg = 'Dropping predictor {}/{} for helpfulness {:.4f} < {:.4f}'\
#                               .format(p.name, p.charname, p_helpfulness, helpfulness_cutoff)
#                     logger.debug(msg)
#
#             npredictors_dropped = len(self._predictors) - len(helpful_predictors)
#             logger.info('Dropped {}/{} predictors for low helpfulness.'\
#                             .format(npredictors_dropped, len(self._predictors)))
#             self._predictors = helpful_predictors


    @staticmethod
    def _get_contribution_count_list():
        return list([0.0, 0])

    def _train(self, training_data, helpfulness_cutoff):
        ''' *training_data* should be of the form: {(id, tone): {charname: charvalue}}
        '''
        for (id, tone), characteristic_values in training_data.items():
            predicted_tone, prediction_score = self.predict(characteristic_values)
            if predicted_tone is not None and predicted_tone != tone:
                self.fail_scores.append(prediction_score)  # *** Is this used?
            elif predicted_tone is not None and predicted_tone == tone:
                self.success_scores.append(prediction_score)

        nno_prediction = 0
        nbad_prediction = 0
        ngood_prediction = 0

        # Keeps track of the score awarded by each predictor for each characteristic
        # This is to provide insight into which predictor/characteristics are most helpful
        #    and which are hurting the accuracy.
        # They are of the form { (<predictor_name>, <charname>): [<contribution>, <contribution_count>] }
        good_contributions = defaultdict(self._get_contribution_count_list)
        bad_contributions = defaultdict(self._get_contribution_count_list)


        for (id, tone), characteristic_values in training_data.items():
            p = self.predict(characteristic_values, id=id)
            predicted_tone = p[0]

            charnames = characteristic_values.keys()

            if predicted_tone is None:
                nno_prediction += 1
            elif predicted_tone is not None and predicted_tone != tone:
                nbad_prediction += 1
                for predictor_name in ['bandpredictor', 'sklearnpredictor']:
                    for charname in charnames:
                        bad_contributions[(predictor_name, charname)][0] += \
                            self.contributions[id][predictor_name][charname][predicted_tone]
                        bad_contributions[(predictor_name, charname)][1] += 1
            elif predicted_tone is not None and predicted_tone == tone:
                ngood_prediction += 1
                for predictor_name in ['bandpredictor', 'sklearnpredictor']:
                    for charname in charnames:
                        good_contributions[(predictor_name, charname)][0] += \
                            self.contributions[id][predictor_name][charname][predicted_tone]
                        good_contributions[(predictor_name, charname)][1] += 1
            else:
                raise Exception('Unexpected logic branch')

    #     with open('consensus_contributions_cache.p', 'wb') as pf:
    #         cPickle.dump(cp.contributions, pf)

        logger.debug('Training: median fail score: {}, median success score: {}'.format(
                      median(self.fail_scores), median(self.success_scores)))

#         total = sum([ngood_prediction, nbad_prediction, nno_prediction])
#         print('Training Prediction Count - Good: {}, Bad: {}, No: {}, Total: {}'.format(
#                  ngood_prediction, nbad_prediction, nno_prediction, total)
#         )

        logger.debug('Contributions:')
        contributions = []
        for predictor_name, charname in good_contributions.keys():
            good = good_contributions[(predictor_name, charname)][0]
            ngood = good_contributions[(predictor_name, charname)][1]

            bad = bad_contributions[(predictor_name, charname)][0]
            nbad = bad_contributions[(predictor_name, charname)][1]

            helpfulness = (good / ngood) - (bad / nbad)

            contributions.append(
                [predictor_name, charname, good, ngood, bad, nbad, helpfulness]
            )

        contributions.sort(key=operator.itemgetter(6))
        logger.debug('Predictor        Characteristic                Good    nGood    Bad     nBad    H1')
        self.helpfulness_by_predictor_charname = {}
        for predictor_name, charname, good, ngood, bad, nbad, helpfulness in contributions:
            if good == 0 and bad == 0: continue

            logger.debug('{: <16} {: <27} {:7.2f} {:7.2f} {:7.2f} {:7.2f} {:7.5f}'\
                    .format(predictor_name, charname, good, ngood, bad, nbad, helpfulness)
            )
            self.helpfulness_by_predictor_charname[(predictor_name, charname)] = helpfulness

    def predict(self, characteristic_values, id=None):
        prediction_scores = defaultdict(float)
        for p in self._predictors:
            if self.helpfulness_cutoff is not None and hasattr(self, 'helpfulness_by_predictor_charname'):
                predictor_helpfulness = self.helpfulness_by_predictor_charname[(p.name, p.charname)]
                if predictor_helpfulness < self.helpfulness_cutoff:
                    continue

            charvalue = characteristic_values.get(p.charname)
            if charvalue is None: continue

            prediction = p.predict(charvalue)
            if prediction is not None:
                for tone in [1, 2, 3, 4, 5]:
                    i = tone - 1

                    if p.accuracy_by_tone[i] <= self.accuracy_cutoff:
                        continue
                    contribution = prediction[i] * p.accuracy_by_tone[i]
                    prediction_scores[tone] += contribution
                    if self.contributions is not None:
                        self.contributions[id][p.name][p.charname][tone] += contribution

        prediction_score = None
        predicted_tone = None
        second_highest = None
        for tone, score in prediction_scores.items():
            if prediction_score is None or score > prediction_score:
                second_highest = prediction_score
                prediction_score = score
                predicted_tone = tone

        # Claim agnostic if there's a tie for the predicted score
        if prediction_score == second_highest:
            predicted_tone = None
            prediction_score = None

        return (predicted_tone, prediction_score)

# These are support fuctions for ConsensusPredictor's "contributions" data structure.
# They are necessary to avoid lambda functions so ConsensusPredictor objects can be pickled.
def _get_float_defaultdict():
    ''' *brief*: Support function for _get_contribution_data_structure() to create
            pickleable defaultdict.
        Its use would look like: tone[tone] += contribution
    '''
    return defaultdict(float)

def _get_charname_tone_defaultdict():
    ''' *brief*: Support function for _get_contribution_data_structure() to create
            pickleable defaultdict.
        Its use would look like: charname_tone[charname][tone] += contribution
    '''
    charname_tone_defaultdict = defaultdict(_get_float_defaultdict)
    return charname_tone_defaultdict

def _get_pname_charname_tone_defaultdict():
    ''' *brief*: Support function for _get_contribution_data_structure() to create
            pickleable defaultdict.
        Its use would look like: pname_charname_tone[pname][charname][tone] += contribution
    '''
    pname_charname_tone_dd = defaultdict(_get_charname_tone_defaultdict)
    return pname_charname_tone_dd

def _get_contribution_data_structure():
    ''' *brief*: Returns a default dict of floats to log score contributions.
        Its useage will look like:
            contributions[id][pname][charname][tone] += contribution
    '''
    contributions = defaultdict(_get_pname_charname_tone_defaultdict)
    return contributions
