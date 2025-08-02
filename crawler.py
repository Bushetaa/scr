import requests
from bs4 import BeautifulSoup
import trafilatura
import time
import random
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from academic_sources import ACADEMIC_SOURCES, EDU_DOMAINS, ORG_DOMAINS, FIELD_KEYWORDS

logger = logging.getLogger(__name__)

class AcademicCrawler:
    def __init__(self, max_workers=5, delay_range=(1, 3)):
        self.max_workers = max_workers
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.crawled_urls = set()
        self.extracted_data = []
        
    def get_page_content(self, url):
        """Extract clean text content from a webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Use trafilatura for clean text extraction
            text_content = trafilatura.extract(response.text)
            
            # Also parse with BeautifulSoup for structured data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'text': text_content,
                'soup': soup,
                'url': url
            }
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, soup, base_url, domain_filter=None):
        """Extract relevant links from a page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Filter by domain if specified
            if domain_filter and domain_filter not in full_url:
                continue
                
            # Skip common non-content URLs
            if any(skip in full_url.lower() for skip in ['login', 'register', 'contact', 'privacy', 'terms']):
                continue
                
            links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def classify_content_field(self, text, url):
        """Classify content into scientific fields based on keywords"""
        text_lower = text.lower() if text else ""
        url_lower = url.lower()
        
        field_scores = {}
        for field, keywords in FIELD_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                score += text_lower.count(keyword.lower())
                if keyword.lower() in url_lower:
                    score += 5  # URL match gets higher weight
            field_scores[field] = score
        
        # Return the field with highest score, or 'علوم عامة' if no clear match
        if max(field_scores.values()) > 0:
            return max(field_scores, key=field_scores.get)
        return 'علوم عامة'
    
    def extract_structured_data(self, content_data):
        """Extract structured academic data from page content"""
        if not content_data or not content_data['text']:
            return None
            
        text = content_data['text']
        soup = content_data['soup']
        url = content_data['url']
        
        # Extract title
        title = None
        for selector in ['h1', 'title', '.title', '.page-title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        if not title:
            title = "محتوى علمي"
        
        # Classify field
        field = self.classify_content_field(text, url)
        
        # Extract key information using regex patterns
        dates = re.findall(r'\b(19|20)\d{2}\b', text)
        
        # Extract names (simple pattern for common academic names)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
        key_people = list(set(names[:5]))  # Limit to 5 unique names
        
        # Create summary (first meaningful paragraph)
        sentences = text.split('.')
        summary = ""
        for sentence in sentences:
            if len(sentence.strip()) > 50 and not sentence.strip().startswith(('http', 'www')):
                summary = sentence.strip()
                break
        
        # Extract facts (sentences with specific patterns)
        facts = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(pattern in sentence.lower() for pattern in ['discovered', 'invented', 'theory', 'law', 'principle']):
                if len(sentence) > 20 and len(sentence) < 200:
                    facts.append(sentence)
                    if len(facts) >= 3:
                        break
        
        # Determine content type
        content_type = "معلومة علمية"
        if any(word in text.lower() for word in ['theory', 'theorem']):
            content_type = "نظرية علمية"
        elif any(word in text.lower() for word in ['experiment', 'study']):
            content_type = "تجربة علمية"
        elif any(word in text.lower() for word in ['discovery', 'invention']):
            content_type = "اكتشاف علمي"
        
        return {
            'type': content_type,
            'title': title[:200],  # Limit title length
            'field': field,
            'date': dates[0] if dates else "",
            'location': "",  # Could be enhanced with location extraction
            'key_people': key_people,
            'summary': summary[:500] if summary else text[:500],  # Limit summary length
            'verified_facts': facts
        }
    
    def crawl_domain(self, domain, max_pages=100):
        """Crawl a specific academic domain"""
        if domain in ACADEMIC_SOURCES:
            source_config = ACADEMIC_SOURCES[domain]
            urls_to_crawl = source_config['base_urls'].copy()
        else:
            # For .edu and .org domains, start with common academic paths
            base_url = f"https://{domain}"
            urls_to_crawl = [
                f"{base_url}/research",
                f"{base_url}/academics",
                f"{base_url}/departments",
                f"{base_url}/science",
                f"{base_url}/publications"
            ]
        
        crawled_count = 0
        domain_data = []
        
        while urls_to_crawl and crawled_count < max_pages:
            current_batch = urls_to_crawl[:self.max_workers]
            urls_to_crawl = urls_to_crawl[self.max_workers:]
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {executor.submit(self.get_page_content, url): url for url in current_batch}
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    if url in self.crawled_urls:
                        continue
                        
                    try:
                        content_data = future.result()
                        if content_data:
                            self.crawled_urls.add(url)
                            crawled_count += 1
                            
                            # Extract structured data
                            structured_data = self.extract_structured_data(content_data)
                            if structured_data:
                                domain_data.append(structured_data)
                            
                            # Extract more links for recursive crawling
                            if crawled_count < max_pages * 0.8:  # Stop finding new links when close to limit
                                new_links = self.extract_links(content_data['soup'], url, domain)
                                for link in new_links[:10]:  # Limit new links per page
                                    if link not in self.crawled_urls and link not in urls_to_crawl:
                                        urls_to_crawl.append(link)
                            
                            logger.info(f"Crawled {crawled_count}/{max_pages} pages from {domain}")
                            
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e}")
                    
                    # Random delay between requests
                    time.sleep(random.uniform(*self.delay_range))
        
        return domain_data
    
    def crawl_all_sources(self, target_count=290000):
        """Crawl all academic sources to reach target count"""
        all_data = []
        
        # Calculate pages per domain to reach target
        total_domains = len(ACADEMIC_SOURCES) + len(EDU_DOMAINS) + len(ORG_DOMAINS)
        pages_per_domain = max(50, target_count // (total_domains * 3))  # Estimate 3 items per page
        
        logger.info(f"Starting crawl with target of {target_count} items")
        logger.info(f"Estimated {pages_per_domain} pages per domain")
        
        # Crawl main academic sources
        for domain in ACADEMIC_SOURCES.keys():
            logger.info(f"Crawling {domain}")
            domain_data = self.crawl_domain(domain, pages_per_domain)
            all_data.extend(domain_data)
            logger.info(f"Extracted {len(domain_data)} items from {domain}")
            
            if len(all_data) >= target_count:
                break
        
        # Crawl .edu domains if we need more data
        if len(all_data) < target_count:
            for domain in EDU_DOMAINS:
                if len(all_data) >= target_count:
                    break
                logger.info(f"Crawling {domain}")
                domain_data = self.crawl_domain(domain, pages_per_domain // 2)
                all_data.extend(domain_data)
                logger.info(f"Extracted {len(domain_data)} items from {domain}")
        
        # Crawl .org domains if we still need more data
        if len(all_data) < target_count:
            for domain in ORG_DOMAINS:
                if len(all_data) >= target_count:
                    break
                logger.info(f"Crawling {domain}")
                domain_data = self.crawl_domain(domain, pages_per_domain // 2)
                all_data.extend(domain_data)
                logger.info(f"Extracted {len(domain_data)} items from {domain}")
        
        # Remove duplicates based on title and summary similarity
        unique_data = self.remove_duplicates(all_data)
        
        logger.info(f"Final count: {len(unique_data)} unique items")
        return unique_data
    
    def remove_duplicates(self, data):
        """Remove duplicate entries based on title similarity"""
        unique_data = []
        seen_titles = set()
        
        for item in data:
            title_key = item['title'].lower().strip()[:100]  # Use first 100 chars for comparison
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_data.append(item)
        
        return unique_data
