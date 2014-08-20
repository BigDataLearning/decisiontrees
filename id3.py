"""
Implements the ID3 algorithm for construction decision trees.

"""

import dtree
import csv
import math
from collections import Counter


class ID3(object):
    def __init__(self, filename):
        self.filename = filename
        self.dtree = None

    def learn(self):
        self.parse_csv()
        self.get_distinct_values()
        self.create_tree()

    def create_tree(self, subset=None, parent=None, parent_value=None):
        """
        Recursively create the decision tree.

        OPTIMIZE: Possibly can be optimized by setting root node at beginning
        """

        # pdb.set_trace()

        # Identify the subset of the data used in the igain calculation
        if subset is None:
            # Initial run, use all data
            subset = self.data
        else:
            # Filter the subset down for the given parent attributes
            subset = self.filter_subset(subset, parent.attribute, parent_value)

        counts = self.attr_counts(subset, self.dependent)
        # If every element in the subset belongs to one dependent group, label
        # with that group.
        if len(counts) == 1:  # Only one value of self.dependent detected
            node = dtree.DTree(
                attribute=counts.keys()[0],
                leaf=True,
                parent_value=parent_value
            )
        elif not self.remaining_attributes:  # OPTIMIZE by setting attribute
            # Also, if there are no remaining attributes, label with the most
            # common attribute in the subset.
            most_common = max(counts, key=lambda k: counts[k])
            node = dtree.DTree(
                attribute=most_common,
                leaf=True,
                parent_value=parent_value
            )
        else:
            igains = []
            for attr in self.remaining_attributes:
                igains.append((attr, self.information_gain(subset, attr)))

            max_attr = max(igains, key=lambda a: a[1])

            # Create the decision tree node
            node = dtree.DTree(
                max_attr[0],
                information_gain=max_attr[1],
                parent_value=parent_value
            )

        if parent is None:
            node.set_attributes(self.attributes)
            self.dtree = node
            # Set known order of attributes for learning
        else:
            parent.add_child(node)

        if not node.leaf:  # Continue recursing
            for value in self.values[node.attribute]:
                self.create_tree(
                    subset=subset,
                    parent=node,
                    parent_value=value
                )

    def parse_csv(self, dependent_index=-1):
        """
        Set the object's attributes and data, where attributes is a list of
        attributes and data is an array of row dictionaries keyed by attribute.

        Also sets the dependent variable, which defaults to the last one

        """

        with open(self.filename) as fin:
            reader = csv.reader(fin)
            attributes = reader.next()
            data = []
            for row in reader:
                row = dict(zip(attributes, row))
                data.append(row)

        self.dependent = attributes[dependent_index]
        self.attributes = [a for a in attributes if a != self.dependent]
        self.all_attributes = attributes
        self.data = data

    def get_distinct_values(self):
        """
        Return a dictionary with attribute keys and sets corresponding to the
        unique items in each attribute.
        """
        values = {}
        for attr in self.all_attributes:  # Use all attributes because ugly
            values[attr] = set(r[attr] for r in self.data)
        self.values = values

    @property
    def distinct_values_list(self):
        values_list = []
        for s in self.values.values():
            for val in s:
                values_list.append(val)
        return values_list

    @property
    def remaining_attributes(self):
        if self.dtree is None:
            return self.attributes
        return [a for a in self.attributes if a not in self.dtree.attributes]

    def filter_subset(self, subset, attr, value):
        """
        Return a subset of the rows of the training data where the given
        attribute has the given value. Used in the recursive construction of
        the decision tree.

        """
        return [r for r in subset if r[attr] == value]

    def information_gain(self, subset, attr):
        gain = self.get_base_entropy(subset)
        occs = self.attr_counts(subset, attr)
        total = float(sum(occs.values()))  # Coerce to float
        for value in self.values[attr]:
            gain += -((occs[value]/total)*self.entropy(subset, attr, value))
        return gain

    def get_base_entropy(self, subset):
        # Not a special case
        return self.entropy(subset, self.dependent, True)

    def entropy(self, subset, attr, value):
        occs = self.value_occurrences(subset, attr, value)
        total = float(sum(occs.values()))  # Coerce to float
        entropy = 0
        for dv in occs:  # For each dependent value
            proportion = occs[dv] / total
            entropy += -(proportion*math.log(proportion, 2))
        return entropy

    def value_occurrences(self, subset, attr, value):
        """
        Return a dictionary (a Counter, specifically) detailing the
        number of occurrences per value of the dependent variable when the
        given attribute is equal to the given value.
        """
        counts = Counter()
        # FIXME: Using subset creates copies unecessarily. Any way to
        # remedy this with a more referential approach?
        for row in subset:
            # This is a terrible check, optimize somehow.
            if row[attr] == value or isinstance(value, bool):
                counts[row[self.dependent]] += 1
        return counts

    def attr_counts(self, subset, attr):
        """
        Return a dictionary (a Counter, specifically) detailing the number of
        occurrences per value of the given attribute
        """
        counts = Counter()
        for row in subset:
            counts[row[attr]] += 1
        return counts

    def __str__(self):
        """
        String representation of the ID3 algorithm assumes user simply wants
        the tree representation.

        """
        return str(id3.dtree)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='name of the .csv file')
    args = parser.parse_args()

    id3 = ID3(args.filename)
    id3.learn()
    print id3
    print id3.dtree.decide(['Rain', 'Mild', 'High', 'Strong'])
    print id3.dtree.decide(['Sunny', 'Mild', 'Normal', 'Strong'])
