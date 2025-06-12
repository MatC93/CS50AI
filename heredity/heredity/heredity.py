import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    """
    We will here show the calculation of joint_probability(people, {"Harry"}, {"James"}, {"James"}). 
    Based on the arguments, one_gene is {"Harry"}, two_genes is {"James"}, and have_trait is {"James"}. 
    This therefore represents the probability that: Lily has 0 copies of the gene and does not have the trait, 
    Harry has 1 copy of the gene and does not have the trait, and James has 2 copies of the gene and does have the trait.
    
    We start with Lily (the order that we consider people does not matter, so long as we multiply the correct values 
    together, since multiplication is commutative). Lily has 0 copies of the gene with probability 0.96 
    (this is PROBS["gene"][0]). Given that she has 0 copies of the gene, she doesn’t have the trait with 
    probability 0.99 (this is PROBS["trait"][0][False]). Thus, the probability that she has 0 copies of the 
    gene and she doesn’t have the trait is 0.96 * 0.99 = 0.9504.

    Next, we consider James. James has 2 copies of the gene with probability 0.01 (this is PROBS["gene"][2]). 
    Given that he has 2 copies of the gene, the probability that he does have the trait is 0.65. 
    Thus, the probability that he has 2 copies of the gene and he does have the trait is 0.01 * 0.65 = 0.0065.

    Finally, we consider Harry. What’s the probability that Harry has 1 copy of the gene? 
    There are two ways this can happen. Either he gets the gene from his mother and not his father, 
    or he gets the gene from his father and not his mother. His mother Lily has 0 copies of the gene, 
    so Harry will get the gene from his mother with probability 0.01 (this is PROBS["mutation"]), 
    since the only way to get the gene from his mother is if it mutated; conversely, 
    Harry will not get the gene from his mother with probability 0.99. His father James has 2 copies of the gene, 
    so Harry will get the gene from his father with probability 0.99 (this is 1 - PROBS["mutation"]), 
    but will get the gene from his mother with probability 0.01 (the chance of a mutation). 
    Both of these cases can be added together to get 0.99 * 0.99 + 0.01 * 0.01 = 0.9802, 
    the probability that Harry has 1 copy of the gene.
    Given that Harry has 1 copy of the gene, the probability that he does not have the trait is 0.44 
    (this is PROBS["trait"][1][False]). So the probability that Harry has 1 copy of the gene and does not 
    have the trait is 0.9802 * 0.44 = 0.431288.

    Therefore, the entire joint probability is just the result of multiplying all of these values for each of the 
    three people: 0.9504 * 0.0065 * 0.431288 = 0.0026643247488.
    """
    probs = 1
    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]
        # probabilità del figlio di non avere il gene:
        # 1) la madre e il padre non gliene passano nessuno
        if person not in one_gene and person not in two_genes:
            if not mother and not father:
                prob = PROBS["gene"][0]
            else:
                prob = 1
                for parent in [mother, father]:
                    if parent not in one_gene and parent not in two_genes:
                        prob *= 0.99
                    elif parent in one_gene:
                        prob *= 0.5
                    else:
                        prob *= 0.01
            if person in have_trait:
                prob *= PROBS["trait"][0][True]
            else:
                prob *= PROBS["trait"][0][False]
        # probabilità del figlio di avere un gene:
        # 1) la madre gliene passa 1 e il padre 0
        # 2) la madre non gliene passa nessuno il padre 1
        elif person in one_gene:
            if not mother and not father:
                prob = PROBS["gene"][1]
            else:
                prob = 0
                for case in [1, 2]:
                    sum_prob = 1
                    if case == 1:
                        if mother not in one_gene and mother not in two_genes:
                            sum_prob *= 0.01
                        elif mother in one_gene:
                            sum_prob *= 0.05
                        else:
                            sum_prob *= 0.99
                        if father not in one_gene and father not in two_genes:
                            sum_prob *= 0.99
                        elif father in one_gene:
                            sum_prob *= 0.5
                        else:
                            sum_prob *= 0.01
                    else:
                        if mother not in one_gene and mother not in two_genes:
                            sum_prob *= 0.99
                        elif mother in one_gene:
                            sum_prob *= 0.05
                        else:
                            sum_prob *= 0.01
                        if father not in one_gene and father not in two_genes:
                            sum_prob *= 0.01
                        elif father in one_gene:
                            sum_prob *= 0.5
                        else:
                            sum_prob *= 0.99
                    prob += sum_prob
            if person in have_trait:
                prob *= PROBS["trait"][1][True]
            else:
                prob *= PROBS["trait"][1][False]
        # probabilità del figlio di avere due geni:
        # 1) la madre e il padre gliene passano uno
        else:
            if not mother and not father:
                prob = PROBS["gene"][2]
            else:
                prob = 1
                for parent in [mother, father]:
                    if parent not in one_gene and parent not in two_genes:
                        prob *= 0.01
                    elif parent in one_gene:
                        prob *= 0.5
                    else:
                        prob *= 0.99
            if person in have_trait:
                prob *= PROBS["trait"][2][True]
            else:
                prob *= PROBS["trait"][2][False]

        probs *= prob
    return probs


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person not in one_gene and person not in two_genes:
            probabilities[person]["gene"][0] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][2] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for key in probabilities[person]:
            normalization = sum(probabilities[person][key].values())
            for value in probabilities[person][key]:
                probabilities[person][key][value] /= normalization


if __name__ == "__main__":
    main()
