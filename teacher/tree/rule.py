# =============================================================================
# Imports
# =============================================================================

# Standard
from collections import defaultdict

# =============================================================================
# Classes
# =============================================================================


class Rule:
    def __init__(self, antecedent, consequent, weight):
        """
        Parameters
        ----------
        antecedent : list of tuples (feature, value)
        consequent : string or number
        weight: weight of the consequent in the tree
        """
        self.antecedent = tuple(antecedent)
        self.consequent = consequent
        self.weight = weight

    def __repr__(self):  # pragma: no cover
        return f'Rule({self.antecedent}, {self.consequent}, {self.weight})'

    def __str__(self):  # pragma: no cover
        antecedents = " AND ".join([f"{feat}: {val}"for (feat, val) in self.antecedent])
        return f'{antecedents} => {self.consequent} (Weight: {self.weight})'

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        return (self.antecedent == other.antecedent and
                self.consequent == other.consequent and
                self.weight == other.weight)

    def matching(self, instance_membership, t_norm=min):
        """Matching that an instance has with the rule
        If there is some feature or value not existing in the instance,
        its matching degree is zero

        Parameters
        ----------
        instance_membership : dict
            Membership of the instance with the format {feature: {value: pertenence degree}}
        t_norm : function, optional
            Operation to use as tnorm to get the matching, by default min
        """
        try:
            return t_norm([instance_membership[feature][value] for (feature, value) in self.antecedent])
        except KeyError:
            return 0

    @staticmethod
    def weighted_vote(rule_list, instance_membership):
        """Use the weighted vote inference method to return the consequent
        associated to an instance and a rule list given the instance membership

        Parameters
        ----------
        rule_list : list[Rule]
            List with the rules that will be taken into account for the
            weighted vote method
        instance_membership : dict
            Membership of the instance with the format
            {feature: {value: pertenence degree}}

        Returns
        -------
        string or number
            consequent associated with the instance and the rule list
        """
        conse_dict = defaultdict(lambda: 0)
        for rule in rule_list:
            AD = rule.matching(instance_membership) * rule.weight
            conse_dict[rule.consequent] += AD
        return max(conse_dict, key=lambda conse: conse_dict[conse])

    @staticmethod
    def map_rule_variables(rule, origin_fuzzy_variables, dest_fuzzy_variables):
        """Changes the fuzzy variables of the rule
        for ones that are defined in the same universe

        Parameters
        ----------
        rule : Rule
            Original rule to map to the new variables
        origin_fuzzy_variables : list[FuzzyVariable]
            List with the original fuzzy variables
        dest_fuzzy_variables : list[FuzzyVariable]
            List with the destination fuzzy variables

        Returns
        -------
        Rule
            Rule with the new variables

        Raises
        ------
        ValueError
            If the universes of the variables are not the same
            it raises an error
        """

        origin_dict = {fv.name: fv.fuzzy_sets for fv in origin_fuzzy_variables}
        dest_dict = {fv.name: fv.fuzzy_sets for fv in dest_fuzzy_variables}

        if origin_dict.keys() != dest_dict.keys():
            raise ValueError('The universes of the fuzzy variables are not the same')

        new_antecedent = []
        for feat, value in rule.antecedent:
            origin_feat = origin_dict[feat]
            dest_feat = dest_dict[feat]

            origin_fuzzy_sets = {fs.name: fs for fs in origin_feat}
            origin_fs = origin_fuzzy_sets[value]

            dest_fs = max(dest_feat, key=lambda fs: fs.intersection(origin_fs))
            new_antecedent.append((feat, dest_fs.name))

        return Rule(new_antecedent, rule.consequent, rule.weight)
