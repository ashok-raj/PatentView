#!/usr/bin/env python3
"""
USPTO Patent Extractor
Retrieves patents where the specified inventor is listed from USPTO's Open Data Portal API
Outputs results in JSON format suitable for LinkedIn API upload
"""

import requests
import json
import sys
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from urllib.parse import quote_plus
import re
from bs4 import BeautifulSoup

class PatentExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.patentsview_url = "https://search.patentsview.org/api/v1/patent/"
        self.google_patents_url = "https://patents.google.com/xhr/query"
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_patents_by_inventor(self, inventor_name: str, assignee_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for patents by inventor name using multiple sources
        """
        patents = []
        
        # Try USPTO PatentsView API if we have a key
        if self.api_key:
            print("Searching USPTO PatentsView API...")
            patents.extend(self._search_patents_view(inventor_name, assignee_name))
        
        # Always search Google Patents as backup/supplement
        print("Searching Google Patents...")
        google_patents = self._search_google_patents(inventor_name, assignee_name)
        patents.extend(google_patents)
        
        return self._remove_duplicates(patents)
    
    def _search_patents_view(self, inventor_name: str, assignee_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search PatentsView API"""
        name_parts = inventor_name.split()
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
        
        query_conditions = [
            {"inventors.inventor_name_first": first_name},
            {"inventors.inventor_name_last": last_name}
        ]
        
        if assignee_name:
            query_conditions.append({"assignees.assignee_organization": assignee_name})
        
        query = {"_and": query_conditions}
        
        params = {
            "q": json.dumps(query),
            "f": json.dumps([
                "patent_id", "patent_title", "patent_date", "patent_abstract",
                "inventors", "assignees"
            ])
        }
        
        headers = {'X-Api-Key': self.api_key}
        
        try:
            response = self.session.get(
                self.patentsview_url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            patents = data.get('patents', [])
            
            # Filter with very strict name and assignee matching
            filtered_patents = []
            inventor_parts = inventor_name.lower().split()
            target_first = inventor_parts[0] if len(inventor_parts) > 0 else ""
            target_last = inventor_parts[-1] if len(inventor_parts) > 1 else inventor_parts[0]
            
            for patent in patents:
                # Check if assignee matches (if specified)
                if assignee_name:
                    assignees = patent.get('assignees', [])
                    assignee_match = False
                    for assignee in assignees:
                        org_name = assignee.get('assignee_organization', '').lower()
                        if assignee_name.lower() in org_name:
                            assignee_match = True
                            break
                    
                    if not assignee_match:
                        continue
                
                # Check for exact inventor name match
                inventors = patent.get('inventors', [])
                inventor_match = False
                
                for inventor in inventors:
                    # Use correct field names from PatentsView API
                    first_name = inventor.get('inventor_name_first', '').lower().strip()
                    last_name = inventor.get('inventor_name_last', '').lower().strip()
                    
                    # Exact match only - no fuzzy matching to avoid name clashes
                    if (first_name == target_first and last_name == target_last):
                        inventor_match = True
                        print(f"✓ Exact match found: {first_name.title()} {last_name.title()} - {patent.get('patent_title', 'Unknown')}")
                        break
                
                if inventor_match:
                    filtered_patents.append(patent)
            
            return self._remove_duplicates(filtered_patents)
            
        except requests.RequestException as e:
            print(f"Error searching PatentsView: {e}")
            return []
    
    def _search_google_patents(self, inventor_name: str, assignee_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search using Google Patents web interface with scraping"""
        # Build search URL
        query = f'inventor:"{inventor_name}"'
        if assignee_name:
            query += f' assignee:"{assignee_name}"'
        
        search_url = f"https://patents.google.com/?q={quote_plus(query)}"
        print(f"Searching: {search_url}")
        
        try:
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            patents = []
            
            # Find search results
            results = soup.find_all('search-result-item') or soup.find_all('article', class_='result')
            
            if not results:
                # Try alternative selectors
                results = soup.find_all('div', {'data-result': True}) or soup.find_all('.search-result-item')
            
            inventor_parts = inventor_name.lower().split()
            target_first = inventor_parts[0] if len(inventor_parts) > 0 else ""
            target_last = inventor_parts[-1] if len(inventor_parts) > 1 else inventor_parts[0]
            
            for result in results[:20]:  # Limit to first 20 results
                try:
                    patent_data = self._extract_patent_from_result(result, target_first, target_last, assignee_name)
                    if patent_data:
                        patents.append(patent_data)
                        print(f"✓ Found: {patent_data.get('patent_title', 'Unknown title')}")
                except Exception as e:
                    print(f"Error parsing result: {e}")
                    continue
            
            if not patents:
                print(f"No matching patents found. Manual search: {search_url}")
            
            return patents
            
        except Exception as e:
            print(f"Error accessing Google Patents: {e}")
            print(f"Manual search URL: {search_url}")
            return []
    
    def _extract_patent_from_result(self, result, target_first: str, target_last: str, assignee_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract patent data from a search result element"""
        
        # Extract title
        title_elem = result.find('h3') or result.find('h4') or result.find('.title')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Extract patent number
        patent_num = ""
        patent_link = result.find('a', href=True)
        if patent_link:
            href = patent_link['href']
            patent_match = re.search(r'patent/([A-Z]{2}\d+[A-Z]\d*)', href)
            if patent_match:
                patent_num = patent_match.group(1)
        
        if not patent_num:
            # Try to find patent number in text
            patent_text = result.get_text()
            patent_match = re.search(r'\b(US\d{7,10}[A-Z]\d*)\b', patent_text)
            if patent_match:
                patent_num = patent_match.group(1)
        
        # Extract abstract/description
        abstract = ""
        desc_elem = result.find('.description') or result.find('.abstract') or result.find('p')
        if desc_elem:
            abstract = desc_elem.get_text(strip=True)[:2000]  # Limit length
        
        # Extract inventors
        inventors = []
        inventor_section = result.find('.inventor') or result.find('.inventors')
        if inventor_section:
            inventor_text = inventor_section.get_text()
            # Parse inventor names
            for name in re.split(r'[,;]', inventor_text):
                name = name.strip()
                if name and len(name.split()) >= 2:
                    parts = name.split()
                    inventors.append({
                        'inventor_name_first': parts[0],
                        'inventor_name_last': parts[-1]
                    })
        
        # Extract assignee
        assignees = []
        assignee_section = result.find('.assignee') or result.find('.applicant')
        if assignee_section:
            assignee_text = assignee_section.get_text(strip=True)
            if assignee_text:
                assignees.append({'assignee_organization': assignee_text})
        
        # Extract date
        date_text = ""
        date_section = result.find('.date') or result.find('.publication-date')
        if date_section:
            date_text = date_section.get_text(strip=True)
        
        # Validate inventor match
        inventor_match = False
        for inv in inventors:
            first = inv.get('inventor_name_first', '').lower()
            last = inv.get('inventor_name_last', '').lower()
            if first == target_first and last == target_last:
                inventor_match = True
                break
        
        # Validate assignee match
        assignee_match = not assignee_name  # If no filter, consider it a match
        if assignee_name:
            for ass in assignees:
                org = ass.get('assignee_organization', '').lower()
                if assignee_name.lower() in org:
                    assignee_match = True
                    break
        
        # Only return if we have minimum required data and matches
        if title and patent_num and inventor_match and assignee_match:
            return {
                'patent_id': patent_num,
                'patent_title': title,
                'patent_abstract': abstract,
                'patent_date': date_text,
                'inventors': inventors,
                'assignees': assignees,
                'source': 'google_patents'
            }
        
        return None
    
    def _remove_duplicates(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate patents based on patent number"""
        seen = set()
        unique_patents = []
        
        for patent in patents:
            patent_num = patent.get('patent_id')  # Updated field name for PatentsView API
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique_patents.append(patent)
                
        return unique_patents
    
    def format_for_linkedin(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format patent data for LinkedIn API upload
        According to LinkedIn Patent Fields Reference
        """
        linkedin_patents = []
        
        for patent in patents:
            # Format the patent for LinkedIn API
            linkedin_patent = {
                "title": patent.get('patent_title', ''),
                "summary": patent.get('patent_abstract', '')[:2000] if patent.get('patent_abstract') else '',  # LinkedIn has character limits
                "number": patent.get('patent_id', ''),
                "status": "granted",  # Assuming granted since we're getting from PatentsView
                "office": {
                    "name": "United States Patent and Trademark Office (USPTO)"
                },
                "inventors": [
                    {
                        "name": f"{inv.get('inventor_name_first', '')} {inv.get('inventor_name_last', '')}".strip()
                    } for inv in patent.get('inventors', [])
                ],
                "date": {
                    "year": int(patent.get('patent_date', '').split('-')[0]) if patent.get('patent_date') else None,
                    "month": int(patent.get('patent_date', '').split('-')[1]) if len(patent.get('patent_date', '').split('-')) > 1 else None,
                    "day": int(patent.get('patent_date', '').split('-')[2]) if len(patent.get('patent_date', '').split('-')) > 2 else None
                },
                "url": f"https://patents.google.com/patent/US{patent.get('patent_id')}" if patent.get('patent_id') else None
            }
            
            # Add assignee if available
            if patent.get('assignees') and len(patent['assignees']) > 0:
                linkedin_patent["assignees"] = [
                    {"name": assignee.get('assignee_organization', '')} 
                    for assignee in patent.get('assignees', [])
                    if assignee.get('assignee_organization')
                ]
            
            # Clean up None values
            linkedin_patent = {k: v for k, v in linkedin_patent.items() if v is not None}
            linkedin_patents.append(linkedin_patent)
        
        return linkedin_patents
    
    def save_to_json(self, patents: List[Dict[str, Any]], filename: str) -> None:
        """Save patents to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(patents, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(patents)} patents to {filename}")
    
    def save_to_csv(self, patents: List[Dict[str, Any]], filename: str) -> None:
        """Save patents to CSV file for manual LinkedIn upload"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Title', 'Patent Number', 'Issue Date', 'Inventors', 
                'Assignee', 'Abstract', 'Google Patents URL'
            ])
            
            # Data rows
            for patent in patents:
                # Format inventors list
                inventors_list = patent.get('inventors', [])
                inventors_str = ', '.join([inv.get('name', '') for inv in inventors_list])
                
                # Format assignees list
                assignees_list = patent.get('assignees', [])
                assignees_str = ', '.join([ass.get('name', '') for ass in assignees_list])
                
                # Format date (just year if full date not available)
                date_obj = patent.get('date', {})
                if isinstance(date_obj, dict):
                    year = date_obj.get('year', '')
                    month = date_obj.get('month', '')
                    day = date_obj.get('day', '')
                    
                    if year and month and day:
                        date_str = f"{year}-{month:02d}-{day:02d}"
                    elif year and month:
                        date_str = f"{year}-{month:02d}"
                    elif year:
                        date_str = str(year)
                    else:
                        date_str = ""
                else:
                    date_str = str(date_obj) if date_obj else ""
                
                # Truncate abstract for CSV
                abstract = patent.get('summary', '')[:500] + '...' if len(patent.get('summary', '')) > 500 else patent.get('summary', '')
                
                writer.writerow([
                    patent.get('title', ''),
                    patent.get('number', ''),
                    date_str,
                    inventors_str,
                    assignees_str,
                    abstract,
                    patent.get('url', '')
                ])
        
        print(f"Saved {len(patents)} patents to CSV: {filename}")
    
    def print_table(self, patents: List[Dict[str, Any]]) -> None:
        """Print patents in a simple table format with summary analysis"""
        if not patents:
            print("No patents to display")
            return
        
        print(f"\n=== Found {len(patents)} Patents ===\n")
        
        # Print header
        print(f"{'Patent Number':<15} {'Title':<80}")
        print("-" * 95)
        
        # Print each patent
        for patent in patents:
            patent_num = patent.get('number', 'N/A')
            title = patent.get('title', 'No title')
            
            # Truncate title if too long
            if len(title) > 77:
                title = title[:74] + "..."
            
            print(f"{patent_num:<15} {title:<80}")
        
        print("-" * 95)
        print(f"Total: {len(patents)} patents")
        
        # Add summary analysis
        self._print_portfolio_summary(patents)
    
    def print_detailed_list(self, patents: List[Dict[str, Any]]) -> None:
        """Print patents in detailed format, one per section"""
        if not patents:
            print("No patents to display")
            return
        
        print(f"\n=== Found {len(patents)} Patents (Detailed View) ===\n")
        
        for i, patent in enumerate(patents, 1):
            print(f"{'='*80}")
            print(f"Patent {i} of {len(patents)}")
            print(f"{'='*80}")
            
            # Title
            title = patent.get('title', 'No title')
            print(f"📄 Title: {title}")
            
            # Patent Number
            patent_num = patent.get('number', 'N/A')
            print(f"🔢 Patent Number: US{patent_num}")
            
            # Inventors
            inventors = patent.get('inventors', [])
            if inventors:
                inventor_names = [inv.get('name', '') for inv in inventors if inv.get('name')]
                if inventor_names:
                    print(f"👥 Inventors: {', '.join(inventor_names)}")
                else:
                    print(f"👥 Inventors: Not available")
            else:
                print(f"👥 Inventors: Not available")
            
            # URL
            url = patent.get('url', '')
            if url:
                print(f"🔗 URL: {url}")
            else:
                print(f"🔗 URL: Not available")
            
            # Abstract
            abstract = patent.get('summary', '')
            if abstract:
                # Word wrap the abstract
                import textwrap
                wrapped_abstract = textwrap.fill(abstract, width=75, initial_indent="📋 Abstract: ", subsequent_indent="            ")
                print(wrapped_abstract)
            else:
                print(f"📋 Abstract: Not available")
            
            # Date
            date_obj = patent.get('date', {})
            if isinstance(date_obj, dict) and date_obj.get('year'):
                year = date_obj.get('year')
                month = date_obj.get('month', '')
                day = date_obj.get('day', '')
                if month and day:
                    print(f"📅 Issue Date: {year}-{month:02d}-{day:02d}")
                else:
                    print(f"📅 Issue Date: {year}")
            else:
                print(f"📅 Issue Date: Not available")
            
            print()  # Empty line between patents
        
        print(f"{'='*80}")
        print(f"Total: {len(patents)} patents")
        
        # Add summary analysis
        self._print_portfolio_summary(patents)
    
    def _print_portfolio_summary(self, patents: List[Dict[str, Any]]) -> None:
        """Print analysis summary of the patent portfolio"""
        if not patents:
            return
        
        # Extract patent numbers and years for range analysis
        patent_nums = []
        years = []
        
        for patent in patents:
            patent_num = patent.get('number', '')
            if patent_num:
                patent_nums.append(patent_num)
                
                # Try to extract year from date
                date_obj = patent.get('date', {})
                if isinstance(date_obj, dict) and date_obj.get('year'):
                    years.append(int(date_obj['year']))
        
        # Categorize patents by technology area based on title keywords
        categories = {
            "Memory & Cache Management": ["memory", "cache", "buffer", "storage", "data transfer"],
            "Virtualization & I/O": ["virtualization", "i/o", "input/output", "translation", "address", "paging"],
            "Error Handling & Machine Check": ["error", "machine check", "fault", "recovery", "exception"],
            "Processor Performance & Interrupts": ["processor", "performance", "interrupt", "cpu", "frequency"],
            "Network Interfaces": ["network", "interface", "communication", "cluster", "protocol"],
            "System Management": ["system", "management", "firmware", "platform", "hardware"]
        }
        
        category_counts = {cat: 0 for cat in categories}
        
        for patent in patents:
            title = patent.get('title', '').lower()
            for category, keywords in categories.items():
                if any(keyword in title for keyword in keywords):
                    category_counts[category] += 1
                    break  # Only count each patent in one category
        
        print(f"\n📊 Patent Portfolio Summary:")
        print(f"• **{len(patents)} total patents**")
        
        if years:
            min_year, max_year = min(years), max(years)
            print(f"• Patent timeline: **{min_year} - {max_year}** ({max_year - min_year + 1} years)")
        
        if patent_nums:
            earliest_num = min(patent_nums, key=lambda x: int(''.join(filter(str.isdigit, x))))
            latest_num = max(patent_nums, key=lambda x: int(''.join(filter(str.isdigit, x))))
            print(f"• Patent numbers range: **{earliest_num}** to **{latest_num}**")
        
        print(f"• Key technology areas:")
        for category, count in category_counts.items():
            if count > 0:
                print(f"  - **{category}** ({count} patents)")
        
        # Calculate innovation rate if we have years
        if len(years) > 1:
            year_range = max(years) - min(years) + 1
            patents_per_year = len(patents) / year_range
            print(f"• Average innovation rate: **{patents_per_year:.1f} patents/year**")

def main():
    parser = argparse.ArgumentParser(description='Extract patents from USPTO for a given inventor')
    parser.add_argument('inventor_name', help='Full name of the inventor (e.g., "Ashok Raj")')
    parser.add_argument('-o', '--output', default='patents.json', help='Output JSON file (default: patents.json)')
    parser.add_argument('--assignee', help='Filter by assignee organization (e.g., "Intel Corporation")')
    parser.add_argument('--api-key', help='USPTO API key (optional)')
    parser.add_argument('--use-google', action='store_true', help='Use Google Patents search instead of USPTO API')
    parser.add_argument('--list', action='store_true', help='Display patents in table format (Patent Number and Title only)')
    parser.add_argument('--detail', action='store_true', help='Display patents in detailed format (Title, Number, Inventors, URL, Abstract)')
    
    args = parser.parse_args()
    
    # Check for conflicting options
    if args.list and args.detail:
        print("Error: Cannot use both --list and --detail options at the same time.")
        return
    
    extractor = PatentExtractor(args.api_key)
    
    search_desc = f"Searching for patents by inventor: {args.inventor_name}"
    if args.assignee:
        search_desc += f" assigned to: {args.assignee}"
    if args.use_google:
        search_desc += " (using Google Patents)"
    print(search_desc)
    
    if args.use_google:
        patents = extractor._search_google_patents(args.inventor_name, args.assignee)
    else:
        patents = extractor.search_patents_by_inventor(args.inventor_name, args.assignee)
    
    if not patents:
        print("No patents found for the specified inventor and assignee.")
        return
    
    # Format for LinkedIn
    linkedin_patents = extractor.format_for_linkedin(patents)
    
    # Display table if requested
    if args.list:
        extractor.print_table(linkedin_patents)
        
        # Save files even in list mode if output specified
        if args.output != 'patents.json':  # Only if user specified custom output
            raw_filename = args.output.replace('.json', '_raw.json')
            extractor.save_to_json(patents, raw_filename)
            
            extractor.save_to_json(linkedin_patents, args.output)
            
            csv_filename = args.output.replace('.json', '.csv')
            extractor.save_to_csv(linkedin_patents, csv_filename)
            
            print(f"\n📁 Files saved:")
            print(f"LinkedIn format: {args.output}")
            print(f"Raw data: {raw_filename}")
            print(f"CSV format: {csv_filename}")
        
        return
    
    # Display detailed view if requested
    if args.detail:
        extractor.print_detailed_list(linkedin_patents)
        
        # Save files even in detail mode if output specified
        if args.output != 'patents.json':  # Only if user specified custom output
            raw_filename = args.output.replace('.json', '_raw.json')
            extractor.save_to_json(patents, raw_filename)
            
            extractor.save_to_json(linkedin_patents, args.output)
            
            csv_filename = args.output.replace('.json', '.csv')
            extractor.save_to_csv(linkedin_patents, csv_filename)
            
            print(f"\n📁 Files saved:")
            print(f"LinkedIn format: {args.output}")
            print(f"Raw data: {raw_filename}")
            print(f"CSV format: {csv_filename}")
        
        return
    
    print(f"Found {len(patents)} unique patents")
    
    # Save raw data
    raw_filename = args.output.replace('.json', '_raw.json')
    extractor.save_to_json(patents, raw_filename)
    
    # Save LinkedIn-formatted data
    extractor.save_to_json(linkedin_patents, args.output)
    
    # Save CSV for manual upload
    csv_filename = args.output.replace('.json', '.csv')
    extractor.save_to_csv(linkedin_patents, csv_filename)
    
    print(f"LinkedIn-formatted patents saved to: {args.output}")
    print(f"Raw data saved to: {raw_filename}")
    print(f"CSV for manual upload saved to: {csv_filename}")

if __name__ == "__main__":
    main()