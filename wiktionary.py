import requests
from bs4 import BeautifulSoup

def get_definition(term, exact=False, subdomain='en',
        language='English', raise_exceptions=False):
    """
    Extracts definitions from wiktionary for a given term while
    excluding extraneous information such as examples, citations,
    quotations, etc.

    Args:
        term (str): the term to search
        exact (bool): 
            if True, searches <term> exactly as entered only
            if False, carries out second search using lower-cased <term>
                if original search is unsuccessful
        subdomain (str): subdomain to prepend to <.wiktionary.org>
            examples: 'en' (English), 'fr' (French), 'simple' (simple
            English)
        language (str): language of definitions (should be set to align
            with subdomain in most cases)
        raise_exceptions (bool):
            if True, raises exceptions when URL is unreachable or
                language section is not found
            if False, returns None in the aforementioned cases

    Returns:
        a dictionary mapping word categories to definitions for <term>

    """
    term = '_'.join(term.split(' '))
    variants = [term,]
    if exact == False:
        variants.append(term.lower())

    for variant in variants:
        response = requests.get(
                f"https://{subdomain}.wiktionary.org/wiki/{variant}")
        if response.ok:
            break

    # For status codes >= 400, return status code
    if not response.ok:
        if raise_exceptions:
            response.raise_for_status() 
        else:
            return None

    # Parse the html
    soup = BeautifulSoup(response.text, 'lxml')

    # Find the relevant section (based on <h2> headers)
    section = None
    h2_tags = soup.find_all(['h2'])
    for h in h2_tags:
        if h.text.startswith(language):
            section = h
            break

    if not section:
        if raise_exceptions:
            raise Exception(f'{language} section not found')
        else:
            return None

    # Find the <ol> tags in the section
    ol_tags = []
    sibling = section.next_sibling
    while sibling and not sibling.name == "h2":
        if sibling.name == "ol":
            ol_tags.append(sibling)
        sibling = sibling.next_sibling

    # Extract the definitions from the <ol> elements
    word_defs = _extract_text(ol_tags)

    return word_defs


def _extract_text(ol_tags, category=None, defs_in_category=[]):
    """
    Extracts the definitions from each ordered list.

    Args: 
        ol_tags: a list of bs4.element.Tag objects for <ol> tags
        category: the current word category (should be None unless
        called recursively)
        defs_in_category: a list of definitions for the current word
        category (should be empty unless called recursively)

    Returns:
        a dictionary mapping word categories to lists of definitions
        (recursive calls modify defs_in_category but return nothing)
    """

    # If category == None, then we are not in a recursive function call, and
    # we should create the main dictionary
    outer = True if not category else False

    if outer:
        word_dict = dict()

    # Loop through the <ol> tags, which are lists of definitions 
    for ol in ol_tags:

        # Find the word category
        word_category = ol.find_previous(['h3']).text.split('[edit]')[0]

        # If a new category is encountered, add a new dictionary entry
        # mapping to a list, and reassign defs_in_category to this list
        if word_category != category:
            category = word_category
            word_dict[category] = []
            defs_in_category = word_dict[category]

        # Loop through the <li> tags, which contain one definition each
        # (sometimes with subdefinitions)
        for child in ol.children:
            if type(child).__name__ == 'Tag' and child.name == "li":
                text = child.text

                # Exclude extra information (examples, citations, etc.)
                # by identifying and removing the text from these items
                subtags_to_exclude = ['ul', 'ol', 'dl']
                kiddies = child.find_all(subtags_to_exclude)
                if kiddies:
                    exclude = child.find(subtags_to_exclude).text
                    idx = text.rfind(exclude)
                    text = text[:idx]

                # Add the definition to our definition list
                defs_in_category.append(text.strip())

                # If we find nested <ol> tags, then the definition
                # contains sub-definitions. This captures them and adds
                # them to the current list of definitions.
                nested_ol_tags = child.find_all(['ol'])
                if nested_ol_tags:
                    _extract_text(nested_ol_tags, category=category,
                            defs_in_category = defs_in_category)

    # Return word_dict only on the outer (non-recursive) instance of
    # this function
    if outer:
        return word_dict
