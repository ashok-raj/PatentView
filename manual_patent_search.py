#!/usr/bin/env python3
"""
Manual Patent Search Helper
Provides direct links and instructions for manual patent searches
"""

import argparse
import webbrowser
from urllib.parse import quote_plus
import csv

def create_search_links(inventor_name: str, assignee_name: str = None):
    """Create search links for multiple patent databases"""
    
    # Google Patents
    google_query = f'inventor:"{inventor_name}"'
    if assignee_name:
        google_query += f' assignee:"{assignee_name}"'
    google_url = f"https://patents.google.com/?q={quote_plus(google_query)}"
    
    # USPTO Public Search
    uspto_query = inventor_name
    if assignee_name:
        uspto_query += f" AND {assignee_name}"
    uspto_url = f"https://ppubs.uspto.gov/pubwebapp/static/pages/ppubsbasic.html"
    
    # Patent Scope (WIPO)
    wipo_query = f"IN:({inventor_name})"
    if assignee_name:
        wipo_query += f" AND AN:({assignee_name})"
    wipo_url = f"https://patentscope.wipo.int/search/en/search.jsf"
    
    links = {
        "Google Patents": google_url,
        "USPTO Public Search": uspto_url,
        "WIPO PatentScope": wipo_url
    }
    
    return links

def print_instructions(inventor_name: str, assignee_name: str = None):
    """Print manual search instructions"""
    
    print(f"\n=== Manual Patent Search for {inventor_name} ===")
    if assignee_name:
        print(f"Assignee filter: {assignee_name}")
    
    links = create_search_links(inventor_name, assignee_name)
    
    print(f"\n📍 Search Links:")
    for name, url in links.items():
        print(f"   {name}: {url}")
    
    print(f"\n📝 Manual Process:")
    print("1. Click each link above to search different patent databases")
    print("2. For each relevant patent found, collect this information:")
    print("   - Patent Title")
    print("   - Patent Number (e.g., US10123456B2)")
    print("   - Issue/Publication Date")
    print("   - All Inventors (verify your name is listed)")
    print("   - Assignee/Applicant")
    print("   - Abstract/Summary")
    print("   - Patent URL")
    
    print(f"\n📊 Data Collection Template:")
    print("Use the CSV template created for easy data entry:")
    print("python3 create_patent_template.py -o manual_patents.csv")
    
    print(f"\n💡 Search Tips:")
    print('• In Google Patents: Use exact search with quotes: inventor:"Ashok Raj"')
    print('• In USPTO: Search by inventor name in the "Inventor Name" field')
    print('• Look for variations of your name (A. Raj, Ashok R., etc.)')
    print('• Filter by assignee/company name to narrow results')
    print('• Check both granted patents and published applications')

def open_search_links(inventor_name: str, assignee_name: str = None):
    """Open search links in web browser"""
    links = create_search_links(inventor_name, assignee_name)
    
    print(f"Opening {len(links)} search links in your browser...")
    for name, url in links.items():
        print(f"Opening {name}...")
        webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description='Manual patent search helper')
    parser.add_argument('inventor_name', help='Full name of the inventor (e.g., "Ashok Raj")')
    parser.add_argument('--assignee', help='Filter by assignee organization (e.g., "Intel Corporation")')
    parser.add_argument('--open-links', action='store_true', help='Open search links in browser')
    parser.add_argument('--create-template', action='store_true', help='Create CSV template for data entry')
    
    args = parser.parse_args()
    
    # Show instructions
    print_instructions(args.inventor_name, args.assignee)
    
    # Open links if requested
    if args.open_links:
        print(f"\n🌐 Opening search links...")
        open_search_links(args.inventor_name, args.assignee)
    
    # Create template if requested
    if args.create_template:
        print(f"\n📝 Creating data entry template...")
        template_filename = f"{args.inventor_name.lower().replace(' ', '_')}_patents.csv"
        create_template(template_filename)

def create_template(filename: str):
    """Create CSV template for manual patent entry"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Patent Title', 'Patent Number', 'Publication Date', 'Issue Date',
            'Inventors', 'Assignee', 'Abstract', 'Patent URL', 'Notes'
        ])
        
        # Example row
        writer.writerow([
            'Example: Method and Apparatus for Processing',
            'US10123456B2',
            '2023-03-15',
            '2023-05-30',
            'Ashok Raj, John Smith',
            'Intel Corporation',
            'A method for improving processor efficiency...',
            'https://patents.google.com/patent/US10123456B2',
            'Key invention for CPU architecture'
        ])
        
        # Empty rows for manual entry
        for i in range(20):
            writer.writerow(['', '', '', '', '', '', '', '', ''])
    
    print(f"Template created: {filename}")

if __name__ == "__main__":
    main()