from itertools import chain, combinations
def powerset(iterable, min_length=0):
    """
    Generate the powerset (i.e. all subsets) of the input iterable with a minimum length.
    :param iterable: The input iterable.
    :param min_length: The minimum length of subsets to generate.
    :return: A generator of subsets.

    Example:
    >>> list(powerset([1, 2, 3, 4], min_length=2))
    [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4), (1, 2, 3, 4)]
    """
    
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(min_length, len(s)+1))

if __name__ == "__main__":
    print(list(powerset([1, 2, 3, 4], min_length=2)))
    "[(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4), (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4), (1, 2, 3, 4)]"