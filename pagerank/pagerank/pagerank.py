import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pages = list(corpus.keys())
    solution = dict.fromkeys(pages, 0)
    num_links = len(corpus[page])
    for link in corpus[page]:
        solution[link] = damping_factor / num_links
    num_pages = len(corpus)
    for page in corpus:
        solution[page] += (1 - damping_factor) / num_pages
    return solution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    hits = dict.fromkeys(pages, 0)
    initial_p = random.choice(pages)
    hits[initial_p] += 1
    probs = transition_model(corpus, initial_p, damping_factor)
    sample_remaining = n - 1
    while sample_remaining > 0:
        samples = random.choices(list(probs.keys()), list(probs.values()), k=1)
        hits[samples[0]] += 1
        probs = transition_model(corpus, samples[0], damping_factor)
        sample_remaining -= 1
    for key in hits:
        hits[key] /= n
    return hits


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    solution = dict.fromkeys(pages, 1 / len(pages))
    differences = dict.fromkeys(pages, 1)
    while any([x > 0.001 for x in differences.values()]):
        for page in pages:
            pages_linked = [x for x in corpus if page in corpus[x]]
            temp = (1 - damping_factor) / len(pages) + \
                   damping_factor * (sum([solution[i] / len(corpus[i]) for i in pages_linked]))
            differences[page] = abs(temp - solution[page])
            solution[page] = temp
    return solution

if __name__ == "__main__":
    main()
