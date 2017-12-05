from collections import defaultdict
from logging import getLogger
from operator import itemgetter
from ttlib.predictors.predictor_base import PredictorBase


logger = getLogger(__name__)

class BandPredictor(PredictorBase):
    ''' This predictor uses a simple concept of identifying the minimum and maximum values that a characteristic
        falls within for each tone.  That range of values [min, max] is the valid "band".
    '''
    name = 'bandpredictor'

    def __init__(self, charname, training_data=None):
        ''' | *brief*: Initialize this predictor.  If training_data is provided it should be an
            |    iterable of 2-tuples (<charvalue>, <tone>) which has already been randomly
            |    ordered.
            |    If it isn't provided it will be extracted from the Characteristic model
            |    using charname.
            | *training_proportion*: The proportion of data to use for training.  The
            |    remainder is used for testing.
        '''
        self.charname = charname
        # These are the differences from the tonal distribution for each charvalue range.
        #    ex {(14, 28): [ -0.14, 0.32, 0.16, -0.08, 0.01 ]
        self.scores_by_band_range = {}

        # These are the accuracies; overall, followed by accuracy for each tone
        self.accuracies = [0] * 6

        scores = self._get_band_scores(training_data)
        self.scores_by_band_range = scores
        accuracies = self._get_accuracies(training_data)
        self.accuracy = accuracies[0]
        self.accuracy_by_tone = accuracies[1:]

    def _get_band_scores(self, train_data):
        """ | *brief*: Trains and tests this predictor using Characteristic instances
            |    with name *charname*.
            | *train_data*: Iterable of 2-tuples (<characteristic value>, <tone>)
            | *returns*: Scores for each band as a dict with the form:
            |    {(band_min, band_max): [ 1 score for each tone ]
        """
        logger.info('BandPredictor(): Training {}'.format(self.charname))
        if len(train_data) == 0:
            raise Exception('zero-length training data provided')

        train_data.sort(key=itemgetter(0))
        len(train_data)
        train_data_tones = [ td[1] for td in train_data ]
        tones = [1, 2, 3, 4, 5]
        tone_counts = [ train_data_tones.count(t) for t in tones ]
        expected_proportions = [
            float(tone_counts[i]) / len(train_data) for i in range(len(tones))
        ]

        # split data into 5% wide chunks and operate on each chunk
        raw_scores_by_band_range = {}
        band_ends = [ int(0.05 * len(train_data) * i) for i in range(1, 21) ]
        for i in range(len(band_ends)):
            band_end = band_ends[i]
            if i == 0:
                band_start = 0
            else:
                band_start = band_ends[i - 1]
            band_data = train_data[band_start:band_end]
            tone_counts = defaultdict(int)
            for v, t in band_data:
                tone_counts[t] += 1

            # This is the amount that the proportion of the tone within the band differs
            #    from the proportion across the entire data set.
            tone_proportions = [
                float(tone_counts[t]) / len(band_data) - expected_proportions[t - 1] for t in tones
            ]

            band_range = (band_data[0][0], band_data[-1][0])
            raw_scores_by_band_range[band_range] = tone_proportions

        return raw_scores_by_band_range

    def _test(self, data):
        accuracies = self._get_accuracies(data)
        self.test_accuracies = accuracies

    def predict(self, charvalue):
        prediction = None
        for (charmin, charmax), scores in self.scores_by_band_range.items():
            if charvalue >= charmin and charvalue < charmax:
                prediction = scores
                break
        return prediction
