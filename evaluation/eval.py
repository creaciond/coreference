import numpy


class Bcubed:
    def __init__(self, cdict, ldict):
        self.cdict = cdict
        self.ldict = ldict

    def mult_precision(self, el1, el2):
        """
        Computes the multiplicity precision for two elements.
        """
        return min(len(self.cdict[el1] & self.cdict[el2]), len(self.ldict[el1] & self.ldict[el2])) \
            / float(len(self.cdict[el1] & self.cdict[el2]))

    def mult_recall(self, el1, el2):
        """
        Computes the multiplicity recall for two elements.
        """
        return min(len(self.cdict[el1] & self.cdict[el2]), len(self.ldict[el1] & self.ldict[el2])) \
            / float(len(self.ldict[el1] & self.ldict[el2]))

    def precision(self):
        """
        Computes overall extended BCubed precision for the C and L dicts.
        """
        return numpy.mean([numpy.mean([self.mult_precision(el1, el2) \
            for el2 in self.cdict if self.cdict[el1] & self.cdict[el2]]) for el1 in self.cdict])

    def recall(self):
        """
        Computes overall extended BCubed recall for the C and L dicts.
        """
        return numpy.mean([numpy.mean([self.mult_recall(el1, el2) \
            for el2 in self.cdict if self.ldict[el1] & self.ldict[el2]]) for el1 in self.cdict])