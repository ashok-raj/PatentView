# USPTO Patent Extractor & LinkedIn Uploader

Two Python programs to extract your patents from USPTO and upload them to your LinkedIn profile.

## Programs

### 1. USPTO Patent Extractor (`uspto_patent_extractor.py`)
Searches for patents where you're listed as an inventor and formats the data for LinkedIn.

**Usage:**
```bash
python3 uspto_patent_extractor.py "Your Full Name" -o patents.json
```

**Features:**
- Uses USPTO's PatentsView API (no API key required)
- Searches by inventor name with fuzzy matching
- Removes duplicate patents
- Outputs both raw USPTO data and LinkedIn-formatted JSON
- Handles patent titles, abstracts, numbers, dates, inventors, and assignees

### 2. LinkedIn Patent Uploader (`linkedin_patent_uploader.py`)
Uploads patent data to your LinkedIn profile via LinkedIn's API.

**Usage:**
```bash
python3 linkedin_patent_uploader.py patents.json --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

**Features:**
- OAuth 2.0 authentication with LinkedIn
- Interactive browser-based login
- Duplicate detection (skips existing patents)
- Rate limiting to respect LinkedIn API limits
- Detailed upload progress and error reporting

## Setup

### Prerequisites
```bash
pip3 install requests
```

### LinkedIn App Setup
1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new app for your personal use
3. Add these redirect URLs:
   - `http://localhost:8080/callback`
4. Request these API permissions:
   - `r_liteprofile` (read basic profile)
   - `w_member_social` (write to profile)
   - `profile:edit` (edit profile sections)
5. Note your Client ID and Client Secret

## Usage Examples

### Extract Patents
```bash
# Extract patents for John Smith
python3 uspto_patent_extractor.py "John Smith" -o john_patents.json

# This creates two files:
# - john_patents.json (LinkedIn-formatted)
# - john_patents_raw.json (raw USPTO data)
```

### Upload to LinkedIn
```bash
# Upload patents to LinkedIn
python3 linkedin_patent_uploader.py john_patents.json \
  --client-id your_linkedin_client_id \
  --client-secret your_linkedin_client_secret

# The program will:
# 1. Open your browser for LinkedIn authentication
# 2. Ask you to paste the authorization code
# 3. Upload patents to your profile
```

## Data Format

The LinkedIn JSON format includes:
```json
{
  "title": "Patent Title",
  "summary": "Patent abstract/description",
  "number": "Patent number",
  "status": "granted",
  "office": {"name": "USPTO"},
  "date": {"year": 2023, "month": 5, "day": 15},
  "url": "https://patents.google.com/patent/US...",
  "inventors": [{"name": "Inventor Name"}],
  "assignees": [{"name": "Company Name"}]
}
```

## Notes

- **USPTO Search**: Uses PatentsView API which is free but may have rate limits
- **LinkedIn Upload**: Requires LinkedIn Developer app and proper OAuth setup
- **Duplicates**: The uploader automatically skips patents already on your profile
- **Rate Limits**: Both programs include delays to respect API limits

## Troubleshooting

### Common Issues
1. **No patents found**: Check spelling of inventor name
2. **LinkedIn auth fails**: Verify app permissions and redirect URLs
3. **Upload errors**: Check LinkedIn API rate limits and field validation

### LinkedIn API Limits
- Be patient between uploads (1 second delay built-in)
- LinkedIn may temporarily block rapid successive API calls
- The program handles most errors gracefully and continues processing