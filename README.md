# USPTO Patent Extractor & LinkedIn Uploader

Python tools to extract patents from USPTO and prepare them for LinkedIn profile upload.

## Programs

### 1. USPTO Patent Extractor (`uspto_patent_extractor.py`)
Searches for patents where you're listed as an inventor and formats the data for LinkedIn.

**Features:**
- Uses USPTO's PatentsView API with exact name matching
- Filters by assignee/company name to avoid false matches
- Multiple output formats: JSON, CSV, table view, detailed view
- Portfolio analysis with technology categorization
- Outputs both raw USPTO data and LinkedIn-formatted data

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
- **Get your key**: https://developer.linkedin.com/
- Create a developer app and request API permissions
- ⚠️ **Warning**: LinkedIn API access is increasingly restrictive for personal use
- Many personal applications are rejected
- Manual upload is recommended instead

## Setup

### Prerequisites
```bash
pip3 install requests beautifulsoup4
```

## Usage Examples

### Complete Patent Extraction Workflow

```bash
# 1. Extract patents with full file generation
python3 uspto_patent_extractor.py "Ashok Raj" \
  --assignee "Intel Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  -o ashok_intel_patents.json

# This creates three files:
# - ashok_intel_patents.json (LinkedIn-formatted)
# - ashok_intel_patents_raw.json (raw USPTO data)  
# - ashok_intel_patents.csv (manual upload format)
```

### Display Options

```bash
# Quick table view (Patent Number + Title)
python3 uspto_patent_extractor.py "Ashok Raj" \
  --assignee "Intel Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --list

# Detailed view (perfect for manual LinkedIn upload)
python3 uspto_patent_extractor.py "Ashok Raj" \
  --assignee "Intel Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --detail

# Detailed view with file saving
python3 uspto_patent_extractor.py "Ashok Raj" \
  --assignee "Intel Corporation" \
  --api-key YOUR_USPTO_API_KEY \
  --detail -o detailed_patents.json
```

### Example Output (Detailed View)
```
=== Found 49 Patents (Detailed View) ===

================================================================================
Patent 1 of 49
================================================================================
📄 Title: Offload data transfer engine for a block data transfer interface
🔢 Patent Number: US10157142
👥 Inventors: Sivakumar Radhakrishnan, Vishal Verma, Chet R. Douglas, Ashok Raj, Narayan Ranganathan, Dan Williams
🔗 URL: https://patents.google.com/patent/US10157142
📋 Abstract: In one embodiment, a block data transfer interface employing
            offload data transfer engine in accordance with the present
            description includes an offload data transfer engine executing...
📅 Issue Date: 2018-12-18

📊 Patent Portfolio Summary:
• **49 total patents**
• Patent timeline: **2004 - 2025** (22 years)
• Key technology areas:
  - **Memory & Cache Management** (12 patents)
  - **Virtualization & I/O** (9 patents)
  - **Error Handling & Machine Check** (10 patents)
• Average innovation rate: **2.2 patents/year**
```

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