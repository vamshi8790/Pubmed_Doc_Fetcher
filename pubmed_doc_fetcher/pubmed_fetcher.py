import requests
import csv
import re
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from xml.etree import ElementTree as ET


@dataclass
class PaperInfo:
    pubmed_id: str
    title: str
    publication_date: str
    non_academic_authors: List[str]
    company_affiliations: List[str]
    corresponding_author_email: str


class PubMedFetcher:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    COMPANY_KEYWORDS = {
        'pfizer', 'roche', 'novartis', 'merck', 'gsk', 'glaxosmithkline',
        'sanofi', 'astrazeneca', 'bristol-myers', 'squibb', 'abbvie',
        'amgen', 'gilead', 'biogen', 'celgene', 'regeneron', 'vertex',
        'moderna', 'biontech', 'illumina', 'thermo fisher', 'danaher',
        'abbott', 'medtronic', 'johnson & johnson', 'j&j', 'eli lilly',
        'boehringer ingelheim', 'takeda', 'bayer', 'pharmaceutical',
        'biotechnology', 'biotech', 'pharma', 'inc.', 'ltd.', 'corp.',
        'corporation', 'limited', 'incorporated'
    }
    
    def __init__(self, email: str = "user@example.com", api_key: Optional[str] = None):
        self.email = email
        self.api_key = api_key
        self.session = requests.Session()
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        search_url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            id_list = root.find('.//IdList')
            
            if id_list is not None:
                return [id_elem.text for id_elem in id_list.findall('Id')]
            return []
            
        except requests.RequestException as e:
            print(f"Error searching papers: {e}")
            return []
        except ET.ParseError as e:
            print(f"Error parsing search results: {e}")
            return []
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[PaperInfo]:
        if not pubmed_ids:
            return []
            
        fetch_url = f"{self.BASE_URL}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pubmed_ids),
            'retmode': 'xml',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
            
        try:
            response = self.session.get(fetch_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            papers = []
            
            for article in root.findall('.//PubmedArticle'):
                paper_info = self._parse_article(article)
                if paper_info:
                    papers.append(paper_info)
                    
            return papers
            
        except requests.RequestException as e:
            print(f"Error fetching paper details: {e}")
            return []
        except ET.ParseError as e:
            print(f"Error parsing paper details: {e}")
            return []
    
    def _parse_article(self, article: ET.Element) -> Optional[PaperInfo]:
        try:
            pubmed_id = article.find('.//PMID').text
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "N/A"
            pub_date = self._extract_publication_date(article)
            non_academic_authors, company_affiliations = self._extract_author_info(article)
            corresponding_email = self._extract_corresponding_email(article)
            
            return PaperInfo(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                non_academic_authors=non_academic_authors,
                company_affiliations=company_affiliations,
                corresponding_author_email=corresponding_email
            )
            
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None
    
    def _extract_publication_date(self, article: ET.Element) -> str:
        date_elements = [
            './/PubDate',
            './/ArticleDate',
            './/DateCompleted'
        ]
        
        for date_path in date_elements:
            date_elem = article.find(date_path)
            if date_elem is not None:
                year = date_elem.find('Year')
                month = date_elem.find('Month')
                day = date_elem.find('Day')
                
                date_parts = []
                if year is not None:
                    date_parts.append(year.text)
                if month is not None:
                    date_parts.append(month.text.zfill(2))
                if day is not None:
                    date_parts.append(day.text.zfill(2))
                
                if date_parts:
                    return '-'.join(date_parts)
        
        return "N/A"
    
    def _extract_author_info(self, article: ET.Element) -> tuple[List[str], List[str]]:
        non_academic_authors = []
        company_affiliations = set()
        
        author_list = article.find('.//AuthorList')
        if author_list is None:
            return [], []
        
        for author in author_list.findall('Author'):
            last_name = author.find('LastName')
            first_name = author.find('ForeName')
            
            if last_name is not None and first_name is not None:
                author_name = f"{first_name.text} {last_name.text}"
            elif last_name is not None:
                author_name = last_name.text
            else:
                continue
            

            affiliations = author.findall('.//Affiliation')
            is_non_academic = False
            
            for affiliation in affiliations:
                if affiliation.text:
                    affiliation_text = affiliation.text.lower()
                    if self._is_company_affiliation(affiliation_text):
                        is_non_academic = True
                        company_affiliations.add(affiliation.text)
            if is_non_academic:
                non_academic_authors.append(author_name)
        
        return non_academic_authors, list(company_affiliations)
    
    def _is_company_affiliation(self, affiliation: str) -> bool:
        affiliation_lower = affiliation.lower()
        for keyword in self.COMPANY_KEYWORDS:
            if keyword in affiliation_lower:
                return True

        academic_keywords = [
            'university', 'college', 'institute', 'school', 'hospital',
            'medical center', 'research center', 'laboratory', 'department'
        ]
        
        has_academic_keyword = any(keyword in affiliation_lower for keyword in academic_keywords)
        
        company_indicators = ['inc', 'ltd', 'corp', 'llc', 'pharmaceutical', 'biotech']
        has_company_indicator = any(indicator in affiliation_lower for indicator in company_indicators)
        
        return has_company_indicator and not has_academic_keyword
    
    def _extract_corresponding_email(self, article: ET.Element) -> str:
        author_list = article.find('.//AuthorList')
        if author_list is None:
            return "N/A"
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for author in author_list.findall('Author'):
            affiliations = author.findall('.//Affiliation')
            for affiliation in affiliations:
                if affiliation.text:
                    emails = re.findall(email_pattern, affiliation.text)
                    if emails:
                        return emails[0]
        
        return "N/A"
    
    def filter_papers_with_company_authors(self, papers: List[PaperInfo]) -> List[PaperInfo]:
        return [paper for paper in papers if paper.non_academic_authors or paper.company_affiliations]
    
    def save_to_csv(self, papers: List[PaperInfo], filename: str) -> None:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'PubmedID', 'Title', 'Publication Date', 
                'Non-academic Author(s)', 'Company Affiliation(s)', 
                'Corresponding Author Email'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for paper in papers:
                writer.writerow({
                    'PubmedID': paper.pubmed_id,
                    'Title': paper.title,
                    'Publication Date': paper.publication_date,
                    'Non-academic Author(s)': '; '.join(paper.non_academic_authors),
                    'Company Affiliation(s)': '; '.join(paper.company_affiliations),
                    'Corresponding Author Email': paper.corresponding_author_email
                })
    
    def fetch_and_filter_papers(self, query: str, max_results: int = 100, 
                               output_file: str = "research_papers.csv") -> List[PaperInfo]:
        print(f"Searching for papers with query: '{query}'")
        pubmed_ids = self.search_papers(query, max_results)
        
        if not pubmed_ids:
            print("No papers found for the given query.")
            return []
        
        print(f"Found {len(pubmed_ids)} papers. Fetching details...")
        all_papers = []
        batch_size = 200
        
        for i in range(0, len(pubmed_ids), batch_size):
            batch_ids = pubmed_ids[i:i + batch_size]
            papers = self.fetch_paper_details(batch_ids)
            all_papers.extend(papers)
            time.sleep(0.34)
        
        print(f"Fetched details for {len(all_papers)} papers.")
        filtered_papers = self.filter_papers_with_company_authors(all_papers)
        print(f"Found {len(filtered_papers)} papers with pharmaceutical/biotech company authors.")
        
        if filtered_papers:
            self.save_to_csv(filtered_papers, output_file)
            print(f"Results saved to {output_file}")
        
        return filtered_papers