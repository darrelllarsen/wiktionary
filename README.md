# wiktionary
Script for scraping definitions from Wiktionary without including superfluous examples, citations, quotations, etc.

Python script for scraping definitions from Wiktionary.

## Basic Usage
Call get_definition with a search term to get a dictionary mapping word categories to lists of definitions.

```
import get_definition from wiktionary

def = get_definition('take')
def['Verb']
```
## Optional Keyword Arguments
subdomain
- subdomain to prepend to `.wiktionary.org` (e.g., 'en', 'fr', 'simple')
- default is 'en'

language
- language section to extract definitions from
- usually should align with subdomain (for maximum results), but could differ in order to extract English translations of homographic words from other languages
  
exact
- if False (default), will search for lower-cased form of search term if the original search failed to return a valid page
  
raise_exceptions
- if False (default), returns None when no definitions are found for any reason
- if True, raises Exceptions for 400-level server responses or failure to extract definitions from pages



  

