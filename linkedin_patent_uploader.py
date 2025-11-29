#!/usr/bin/env python3
"""
LinkedIn Patent Uploader
Uploads patent data to LinkedIn profile via LinkedIn API
Uses OAuth 2.0 for authentication and LinkedIn Profile Edit API for patent management
"""

import requests
import json
import sys
import argparse
from typing import List, Dict, Any, Optional
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import time
from datetime import datetime

class LinkedInPatentUploader:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.api_base = "https://api.linkedin.com/v2"
        self.session = requests.Session()
        
        # LinkedIn OAuth URLs
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        # Required scopes for patent management
        self.scopes = ["r_liteprofile", "w_member_social", "profile:edit"]
        
    def get_authorization_url(self, redirect_uri: str) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "state": "patent_upload_session"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> bool:
        """Exchange authorization code for access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = self.session.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            if self.access_token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                return True
            
        except requests.RequestException as e:
            print(f"Error exchanging code for token: {e}")
            
        return False
    
    def authenticate_interactive(self) -> bool:
        """Interactive OAuth flow for getting access token"""
        redirect_uri = "http://localhost:8080/callback"
        
        auth_url = self.get_authorization_url(redirect_uri)
        
        print("\n=== LinkedIn Authentication Required ===")
        print("1. A browser window will open with LinkedIn's authorization page")
        print("2. Log in to LinkedIn and authorize the application")
        print("3. You'll be redirected to a localhost page")
        print("4. Copy the 'code' parameter from the URL and paste it below")
        print("\nOpening browser...")
        
        webbrowser.open(auth_url)
        
        print(f"\nIf the browser didn't open, visit this URL:\n{auth_url}\n")
        
        code = input("Enter the authorization code from the redirect URL: ").strip()
        
        if self.exchange_code_for_token(code, redirect_uri):
            print("✓ Authentication successful!")
            return True
        else:
            print("✗ Authentication failed")
            return False
    
    def get_profile_id(self) -> Optional[str]:
        """Get the current user's LinkedIn profile ID"""
        try:
            response = self.session.get(f"{self.api_base}/people/~")
            response.raise_for_status()
            
            profile_data = response.json()
            return profile_data.get("id")
            
        except requests.RequestException as e:
            print(f"Error getting profile ID: {e}")
            return None
    
    def get_existing_patents(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get existing patents from LinkedIn profile"""
        try:
            response = self.session.get(
                f"{self.api_base}/people/{profile_id}/patents",
                headers={"X-Restli-Protocol-Version": "2.0.0"}
            )
            response.raise_for_status()
            
            return response.json().get("elements", [])
            
        except requests.RequestException as e:
            print(f"Error getting existing patents: {e}")
            return []
    
    def create_patent(self, profile_id: str, patent_data: Dict[str, Any]) -> bool:
        """Create a new patent entry on LinkedIn profile"""
        
        # Format patent data for LinkedIn API
        linkedin_patent = {
            "title": patent_data.get("title", ""),
            "summary": patent_data.get("summary", ""),
            "number": patent_data.get("number", ""),
            "status": patent_data.get("status", "granted"),
            "office": patent_data.get("office", {"name": "USPTO"}),
            "date": patent_data.get("date", {})
        }
        
        # Add optional fields if present
        if patent_data.get("url"):
            linkedin_patent["url"] = patent_data["url"]
            
        if patent_data.get("inventors"):
            linkedin_patent["inventors"] = patent_data["inventors"]
            
        if patent_data.get("assignees"):
            linkedin_patent["assignees"] = patent_data["assignees"]
        
        try:
            response = self.session.post(
                f"{self.api_base}/people/{profile_id}/patents",
                json=linkedin_patent,
                headers={"X-Restli-Protocol-Version": "2.0.0"}
            )
            response.raise_for_status()
            
            print(f"✓ Successfully uploaded: {patent_data.get('title', 'Unknown')}")
            return True
            
        except requests.RequestException as e:
            print(f"✗ Error uploading patent '{patent_data.get('title', 'Unknown')}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    print(f"  Details: {error_details}")
                except:
                    print(f"  Response: {e.response.text}")
            return False
    
    def upload_patents(self, patents: List[Dict[str, Any]], skip_duplicates: bool = True) -> Dict[str, int]:
        """Upload multiple patents to LinkedIn profile"""
        
        profile_id = self.get_profile_id()
        if not profile_id:
            return {"success": 0, "failed": 0, "skipped": 0}
        
        existing_patents = []
        if skip_duplicates:
            existing_patents = self.get_existing_patents(profile_id)
            existing_numbers = {p.get("number", "") for p in existing_patents}
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for patent in patents:
            patent_number = patent.get("number", "")
            
            # Check for duplicates
            if skip_duplicates and patent_number in existing_numbers:
                print(f"⚠ Skipping duplicate: {patent.get('title', 'Unknown')} ({patent_number})")
                results["skipped"] += 1
                continue
            
            # Rate limiting - LinkedIn has API rate limits
            time.sleep(1)
            
            if self.create_patent(profile_id, patent):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def validate_patents_format(self, patents: List[Dict[str, Any]]) -> bool:
        """Validate that patents are in the correct format for LinkedIn"""
        required_fields = ["title", "number"]
        
        for i, patent in enumerate(patents):
            for field in required_fields:
                if not patent.get(field):
                    print(f"Error: Patent {i+1} missing required field: {field}")
                    return False
        
        return True

def load_patents_from_file(filename: str) -> List[Dict[str, Any]]:
    """Load patents from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {filename}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Upload patents to LinkedIn profile')
    parser.add_argument('patents_file', help='JSON file containing patent data')
    parser.add_argument('--client-id', required=True, help='LinkedIn app client ID')
    parser.add_argument('--client-secret', required=True, help='LinkedIn app client secret')
    parser.add_argument('--no-skip-duplicates', action='store_true', 
                       help='Do not skip patents that already exist on profile')
    
    args = parser.parse_args()
    
    # Load patents from file
    patents = load_patents_from_file(args.patents_file)
    if not patents:
        return
    
    print(f"Loaded {len(patents)} patents from {args.patents_file}")
    
    # Initialize uploader
    uploader = LinkedInPatentUploader(args.client_id, args.client_secret)
    
    # Validate patent format
    if not uploader.validate_patents_format(patents):
        print("Error: Patents file format is invalid")
        return
    
    # Authenticate
    if not uploader.authenticate_interactive():
        print("Authentication failed. Cannot proceed with upload.")
        return
    
    # Upload patents
    print(f"\nUploading {len(patents)} patents to LinkedIn...")
    results = uploader.upload_patents(patents, skip_duplicates=not args.no_skip_duplicates)
    
    # Print results
    print(f"\n=== Upload Results ===")
    print(f"Successfully uploaded: {results['success']}")
    print(f"Failed uploads: {results['failed']}")
    print(f"Skipped duplicates: {results['skipped']}")
    print(f"Total processed: {sum(results.values())}")

if __name__ == "__main__":
    main()