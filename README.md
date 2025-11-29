# USPTO Patent Extractor & LinkedIn Uploader

Python tools to extract patents from USPTO and prepare them for LinkedIn profile upload.

## Programs

### 1. USPTO Patent Extractor (`uspto_patent_extractor.py`)
Searches for patents where you're listed as an inventor and formats the data for LinkedIn.

**Features:**
- Uses USPTO's PatentsView API with exact name matching (fuzzy matching has limitations)
- Filters by assignee/company name to avoid false matches
- Multiple output formats: JSON, CSV, table view, detailed view
- Portfolio analysis with technology categorization
- Experimental fuzzy matching (limited by API data coverage)
- Outputs both raw USPTO data and LinkedIn-formatted data

**⚠️ API Limitations:**
- PatentsView API has incomplete inventor indexing - not all co-inventors are searchable
- Some inventors appear in patent details but aren't indexed for direct search
- Recommended approach: Search known collaborators and examine co-inventor lists

### 2. LinkedIn Patent Uploader (`linkedin_patent_uploader.py`)
⚠️ **UNTESTED** - Uploads patent data to your LinkedIn profile via LinkedIn's API.

**Important Notes:**
- This tool is **untested** due to LinkedIn API restrictions
- LinkedIn has become very restrictive with API access for personal use
- Getting LinkedIn API keys is increasingly difficult
- Manual upload is recommended as primary method

## API Keys Required

### USPTO PatentsView API Key
**Required** for patent extraction:
- **Get your key**: https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18
- Submit a request via email and wait for API key response
- Free access to comprehensive USPTO patent database

### LinkedIn API Key (Optional)
**Optional** for automated LinkedIn upload:
- **Apply for API access**: https://developer.linkedin.com/
- **Documentation**: https://learn.microsoft.com/en-us/linkedin/
- **Application process**:
  1. Create a LinkedIn Developer account
  2. Create a new app at https://www.linkedin.com/developers/apps
  3. Request "Profile API" and "Marketing Developer Platform" products
  4. Wait for approval (can take several days)
- ⚠️ **Warning**: LinkedIn API access is increasingly restrictive for personal use
- Many personal applications are rejected without business justification
- Manual upload is recommended as the primary method

## Setup

### Prerequisites
```bash
pip3 install requests beautifulsoup4
```

## Usage Examples

### Complete Patent Extraction Workflow

```bash
# 1. Extract patents with full file generation
python3 uspto_patent_extractor.py "John Smith" \
  --assignee "Tech Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  -o john_patents.json

# This creates three files:
# - john_patents.json (LinkedIn-formatted)
# - john_patents_raw.json (raw USPTO data)  
# - john_patents.csv (manual upload format)
```

### Display Options

```bash
# Quick table view (Patent Number + Title)
python3 uspto_patent_extractor.py "Jane Doe" \
  --assignee "Tech Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --list

# Detailed view (perfect for manual LinkedIn upload)
python3 uspto_patent_extractor.py "Jane Doe" \
  --assignee "Tech Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --detail

# Detailed view with file saving
python3 uspto_patent_extractor.py "Jane Doe" \
  --assignee "Tech Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --detail -o detailed_patents.json

# Fuzzy matching for names with middle initials
python3 uspto_patent_extractor.py "John Smith" \
  --assignee "Tech Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --fuzzy --list
# This will find "John M. Smith", "John A. Smith", etc.
```

### Example Output (Detailed View)
```
=== Found 25 Patents (Detailed View) ===

================================================================================
Patent 1 of 25
================================================================================
📄 Title: Method and apparatus for data processing optimization
🔢 Patent Number: US10123456
👥 Inventors: Jane Doe, John Smith, Alice Johnson
🔗 URL: https://patents.google.com/patent/US10123456
📋 Abstract: A system and method for optimizing data processing operations
            in distributed computing environments. The invention provides
            improved performance through novel algorithmic approaches...
📅 Issue Date: 2023-03-15

📊 Patent Portfolio Summary:
• **25 total patents**
• Patent timeline: **2015 - 2023** (9 years)
• Key technology areas:
  - **Data Processing & Algorithms** (8 patents)
  - **Distributed Systems** (6 patents)
  - **Machine Learning** (5 patents)
  - **Network Security** (4 patents)
  - **User Interface Design** (2 patents)
• Average innovation rate: **2.8 patents/year**
```

### Fuzzy Name Matching

⚠️ **Limited Effectiveness** - The `--fuzzy` option has known limitations due to USPTO API constraints:

```bash
# Fuzzy search attempts (may not work as expected)
python3 uspto_patent_extractor.py "John Smith" --api-key YOUR_KEY --fuzzy --list
python3 uspto_patent_extractor.py "Robert Johnson" --api-key YOUR_KEY --fuzzy --list
```

**How fuzzy matching works (when functional):**
- Uses USPTO's `_text_any` operator to search full inventor names
- Attempts partial matching for names with middle initials
- Falls back to exact field matching if text search fails

**Known limitations:**
- ❌ **API data gaps**: USPTO PatentsView API has incomplete inventor indexing
- ❌ **Co-inventor search issues**: Many co-inventors aren't indexed for primary search
- ❌ **Inconsistent results**: Same inventor may appear in patent details but not be searchable
- ❌ **Server errors**: Complex queries sometimes cause 500 server errors

**Recommended workaround for finding co-inventors:**
1. Search patents of known collaborators (who do have indexed patents)
2. Examine co-inventor lists in the detailed output
3. Use the exact spelling found in those lists for subsequent searches

```bash
# Example: Find co-inventors by searching a known inventor
python3 uspto_patent_extractor.py "Known Collaborator" --api-key YOUR_KEY --detail
# Look at the inventor lists to find exact spellings of other inventors
```

**When fuzzy search may help:**
- ✅ For inventors who already have some patents indexed in the API
- ✅ For simple name variations without complex middle initials
- ⚠️ Not reliable for comprehensive co-inventor discovery

### Manual LinkedIn Upload (Recommended)
The detailed view format makes manual LinkedIn upload easy:

1. Run with `--detail` option to see full patent information
2. Copy the patent details from terminal output
3. Manually add each patent to your LinkedIn profile:
   - Patent Title → Copy from "📄 Title"
   - Patent Number → Copy from "🔢 Patent Number"  
   - Patent URL → Copy from "🔗 URL"
   - Inventors → Copy from "👥 Inventors"
   - Abstract → Copy from "📋 Abstract" (trim to LinkedIn limits)

### LinkedIn API Upload (Untested)
```bash
# ⚠️ UNTESTED - Use at your own risk
python3 linkedin_patent_uploader.py patents.json \
  --client-id your_linkedin_client_id \
  --client-secret your_linkedin_client_secret
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