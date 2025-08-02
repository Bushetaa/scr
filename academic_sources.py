"""
Configuration for academic sources and their specific crawling patterns
"""

ACADEMIC_SOURCES = {
    'britannica.com': {
        'base_urls': [
            'https://www.britannica.com/science/physics',
            'https://www.britannica.com/science/chemistry',
            'https://www.britannica.com/science/mathematics',
            'https://www.britannica.com/science/biology',
            'https://www.britannica.com/topic/history',
            'https://www.britannica.com/science/astronomy',
            'https://www.britannica.com/science/geology',
            'https://www.britannica.com/technology/computer-science'
        ],
        'selectors': {
            'title': 'h1.md-title',
            'content': '.md-article-container',
            'links': 'a[href*="/"]'
        },
        'field_mapping': {
            'physics': 'فيزياء',
            'chemistry': 'كيمياء',
            'mathematics': 'رياضيات',
            'biology': 'أحياء',
            'history': 'تاريخ',
            'astronomy': 'فلك',
            'geology': 'علوم الأرض',
            'computer-science': 'حاسوب'
        }
    },
    'nasa.gov': {
        'base_urls': [
            'https://www.nasa.gov/mission/',
            'https://www.nasa.gov/solar-system/',
            'https://www.nasa.gov/universe/',
            'https://science.nasa.gov/'
        ],
        'selectors': {
            'title': 'h1',
            'content': '.uswds-prose',
            'links': 'a[href*="nasa.gov"]'
        },
        'field_mapping': {
            'mission': 'فلك',
            'solar-system': 'فلك',
            'universe': 'فلك',
            'science': 'علوم فضاء'
        }
    },
    'science.org': {
        'base_urls': [
            'https://www.science.org/topic/article-type/research-article',
            'https://www.science.org/topic/physical-sciences',
            'https://www.science.org/topic/life-sciences',
            'https://www.science.org/topic/earth-environmental-sciences'
        ],
        'selectors': {
            'title': 'h1.page-title',
            'content': '.article__body',
            'links': 'a[href*="science.org"]'
        },
        'field_mapping': {
            'physical-sciences': 'فيزياء',
            'life-sciences': 'أحياء',
            'earth-environmental-sciences': 'علوم الأرض',
            'research-article': 'علوم عامة'
        }
    },
    'nist.gov': {
        'base_urls': [
            'https://www.nist.gov/physics',
            'https://www.nist.gov/chemistry',
            'https://www.nist.gov/material-science'
        ],
        'selectors': {
            'title': 'h1',
            'content': '.field-item',
            'links': 'a[href*="nist.gov"]'
        },
        'field_mapping': {
            'physics': 'فيزياء',
            'chemistry': 'كيمياء',
            'material-science': 'علوم المواد'
        }
    }
}

# Educational domains to target
EDU_DOMAINS = [
    'mit.edu',
    'stanford.edu',
    'harvard.edu',
    'caltech.edu',
    'princeton.edu',
    'yale.edu',
    'berkeley.edu',
    'columbia.edu'
]

# Scientific organizations
ORG_DOMAINS = [
    'nih.gov',
    'nsf.gov',
    'energy.gov',
    'usgs.gov',
    'noaa.gov',
    'cdc.gov'
]

FIELD_KEYWORDS = {
    'فيزياء': ['physics', 'quantum', 'relativity', 'mechanics', 'thermodynamics', 'electromagnetic'],
    'كيمياء': ['chemistry', 'chemical', 'molecule', 'compound', 'reaction', 'periodic table'],
    'رياضيات': ['mathematics', 'algebra', 'calculus', 'geometry', 'statistics', 'theorem'],
    'أحياء': ['biology', 'DNA', 'cell', 'anatomy', 'genetics', 'evolution'],
    'تاريخ': ['history', 'ancient', 'civilization', 'war', 'empire', 'dynasty'],
    'فلك': ['astronomy', 'planet', 'star', 'galaxy', 'universe', 'cosmology'],
    'علوم الأرض': ['geology', 'earth science', 'climate', 'weather', 'ocean', 'atmosphere'],
    'حاسوب': ['computer science', 'algorithm', 'programming', 'software', 'artificial intelligence'],
    'تغذية': ['nutrition', 'diet', 'vitamin', 'mineral', 'food science'],
    'بيئة': ['environment', 'ecology', 'conservation', 'sustainability', 'pollution']
}
