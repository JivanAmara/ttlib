'''
Created on Jul 1, 2016

@author: jivan
'''
from numpy import average


class PredictorBase(object):
    name = None

    def _get_accuracies(self, data):
        ''' Returns a length-6 list of accuracies in the range [0, 1].
            accuracies[0] is the overall accuracy accuracies[1-5] are the accuracies for
            individual tones.
        '''
        # correct_counts[0] is overall correct correct_counts[1:6] is correct for each tone
        # same scheme for overall_counts
        correct_counts = [0.0] * 6
        overall_counts = [0.0] * 6

        for charvalue, tone in data:
            prediction = self.predict(charvalue)
            if prediction is None: continue

            predicted_tones = []
            max_score = max(prediction)
            for i in range(5):
                if prediction[i] == max_score:
                    predicted_tones.append(i + 1)

            if tone in predicted_tones:
                # If the prediction selects more than one potential candidate,
                #    distribute the point among the candidates.
                shared_correct = 1.0 / len(predicted_tones)
                correct_counts[0] += shared_correct
                for predicted_tone in predicted_tones:
                    correct_counts[predicted_tone] += shared_correct

            overall_counts[0] += 1.0
            for predicted_tone in predicted_tones:
                overall_counts[predicted_tone] += 1.0

        accuracies = [
            0 if correct_counts[t] == 0 else float(correct_counts[t]) / overall_counts[t]
                for t in range(6)
        ]

        return accuracies

    def _get_normalized_scores(self, scores):
        ''' | *brief*: Scales & translates *scores* so the sum of the values equals 0 and
            |    all values are in the range [-1, 1]
            *scores* is a list/tuple of 5 floating point numbers specifying how much weight
                a predictor gives to each of the 5 tones.
        '''
        # Balance the scores so they total to 0
        midpoint = average(scores)
        balanced_scores = [ s - midpoint for s in scores ]
        greatest_magnitude = max([ abs(s) for s in balanced_scores ])
        normalized_scores = [ s / greatest_magnitude for s in balanced_scores ]
        return normalized_scores

    def _test(self, data):
        accuracies = self._get_accuracies(data)
        self.test_accuracies = accuracies


