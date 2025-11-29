#!/usr/bin/env python3
"""
Patent Template Generator
Creates a CSV template for manually entering patent data for LinkedIn upload
"""

import csv
import argparse

def create_template(filename: str, num_rows: int = 5):
    """Create a CSV template with sample/empty rows for manual patent entry"""
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Title', 'Patent Number', 'Issue Date', 'Inventors', 
            'Assignee', 'Abstract', 'Google Patents URL'
        ])
        
        # Sample row for reference
        writer.writerow([
            'Method and Apparatus for Dynamic CPU Frequency Scaling',
            'US10123456B2',
            '2023-05-15',
            'Ashok Raj, John Smith, Jane Doe',
            'Intel Corporation',
            'A system and method for dynamically adjusting processor frequency based on workload demand...',
            'https://patents.google.com/patent/US10123456B2'
        ])
        
        # Empty rows for manual entry
        for i in range(num_rows):
            writer.writerow(['', '', '', '', '', '', ''])
    
    print(f"Created patent template: {filename}")
    print("\nInstructions:")
    print("1. Search Google Patents manually using the URL provided")
    print("2. Fill in the patent details in the CSV template")
    print("3. Copy/paste data from CSV to LinkedIn when adding patents manually")
    print("\nCSV Format:")
    print("- Title: Full patent title")
    print("- Patent Number: US patent number (e.g., US10123456B2)")
    print("- Issue Date: YYYY-MM-DD format")
    print("- Inventors: Comma-separated list")
    print("- Assignee: Company name")
    print("- Abstract: Brief description (keep under 2000 chars)")
    print("- URL: Google Patents link")

def main():
    parser = argparse.ArgumentParser(description='Create patent entry template')
    parser.add_argument('-o', '--output', default='patent_template.csv', 
                       help='Output CSV file (default: patent_template.csv)')
    parser.add_argument('-n', '--num-rows', type=int, default=10,
                       help='Number of empty rows to create (default: 10)')
    
    args = parser.parse_args()
    
    create_template(args.output, args.num_rows)

if __name__ == "__main__":
    main()