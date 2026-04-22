# 🏦 Bank PII Leak Detector (TikTok) — n8n Workflow

> An automated AI-powered pipeline that monitors TikTok for bank-related content and flags any **Personally Identifiable Information (PII)** leaks using computer vision — built with n8n, Groq, and Google Sheets.

---

## 📌 Overview

Banks and their employees sometimes post videos on TikTok that accidentally expose sensitive information — computer screens showing account details, CNIC/ID cards, restricted documents, etc. This workflow **automates the detection of such leaks** by:

1. Searching TikTok for bank-related keywords (Pakistan region)
2. Extracting video thumbnails and metadata
3. Sending thumbnails to a **multimodal AI (Groq + LLaMA 4 Scout)** for vision analysis
4. Filtering only results where PII/data leaks are detected
5. Logging all flagged videos into a **Google Sheet** for review and responsible disclosure

---

## 🔄 Workflow Architecture

```
Manual Trigger
     │
     ▼
Scrape TikTok (RapidAPI)       ← Search "bank duty pakistan" in Pakistan region
     │
     ▼
Split Videos                   ← Expand array of results into individual items
     │
     ▼
Save Metadata                  ← Extract: username, display name, description,
     │                            video ID, cover URL, likes, views, created date
     ▼
Limit (5 items)               ← Cap to 5 videos per run (rate limit protection)
     │
     ▼
Groq Vision AI                ← POST to Groq API with thumbnail image URL
     │                            Model: meta-llama/llama-4-scout-17b-16e-instruct
     │                            Prompt: Detect PII, CNICs, screens, documents
     ▼
Filter: PII Detected?         ← Regex match on AI response for leak keywords
     │                            (only proceeds if leak is found)
     ▼
Google Sheets                 ← Append flagged entry with all metadata + AI caption
```

---

## 🧩 Nodes Breakdown

| Node | Type | Purpose |
|------|------|---------|
| **When clicking 'Execute workflow'** | Manual Trigger | Starts the workflow on demand |
| **Scrape TikTok (RapidAPI)** | HTTP Request | Queries TikTok Search API via RapidAPI for videos matching the keyword |
| **Split Videos** | Item Lists | Splits the returned `item_list` array into individual video items |
| **Save Metadata** | Set | Maps raw TikTok API fields to clean, named fields |
| **Limit** | Limit | Restricts processing to 5 videos per run to avoid rate-limit errors |
| **Groq Vision AI** | HTTP Request | Sends thumbnail image URL to Groq's multimodal LLM for PII analysis |
| **Filter: PII Detected?** | Filter | Regex-filters AI responses for 20+ PII/leak-related keywords |
| **Google Sheets** | Google Sheets | Appends flagged records to a tracking spreadsheet |

---

## 🤖 AI Analysis Details

### Model
- **Provider:** [Groq](https://groq.com/)
- **Model:** `meta-llama/llama-4-scout-17b-16e-instruct` (vision-capable)
- **Max Tokens:** 150

### Prompt Strategy
The model is given the video thumbnail and asked:
> *"Analyze this image. State ONLY if there is any visible PII breach, data leak, or possible chance of it (like exposed computer screens, restricted documents, CNICs, ID cards, account numbers, email addresses, forms, or bank cards). If NO leak/breach is visible, reply EXACTLY with 'No leak'. If YES, briefly describe the exposed information."*

### PII Filter Keywords (Regex)
The filter node checks AI responses against:
```
cnic | national id | passport | restrict | confidential | document | form |
screen | computer | email | account | statement | card | atm | teller |
cash | money | cheque | check | sensitive | pii | leak | breach | exposed
```

---

## 📊 Google Sheets Output Schema

When a PII leak is detected, the following columns are written to `Sheet1`:

| Column | Description |
|--------|-------------|
| `Date` | ISO timestamp of when the record was logged |
| `TikTok Username` | Creator's unique TikTok handle |
| `Display Name` | Creator's display name |
| `Video Description` | Caption/description of the video |
| `Video URL` | Direct link to the TikTok video |
| `Thumbnail URL` | URL of the video cover image analyzed by AI |
| `AI Caption (What Is Visible)` | AI's description of the detected PII |
| `Likes` | Like count at time of detection |
| `Views` | View count at time of detection |
| `Video Created At` | Unix timestamp when the video was posted |

---

## ⚙️ Setup & Configuration

### Prerequisites
- [n8n](https://n8n.io/) instance (self-hosted or cloud)
- [RapidAPI](https://rapidapi.com/) account with access to **TikTok API23**
- [Groq API](https://console.groq.com/) key with a vision-capable model enabled
- Google account with a target **Google Sheet** created

### Step-by-Step Setup

#### 1. Import the Workflow
1. Open your n8n instance
2. Go to **Workflows → Import from File**
3. Select `Bank PII Leak Detector (TikTok).json`

#### 2. Configure API Keys

> ⚠️ **Never commit real API keys to GitHub.** Replace placeholders before using.

| Node | Credential to Set |
|------|------------------|
| `Scrape TikTok (RapidAPI)` | Set `x-rapidapi-key` header to your RapidAPI key |
| `Groq Vision AI` | Set `Authorization: Bearer <YOUR_GROQ_API_KEY>` header |
| `Google Sheets` | Configure Google Sheets OAuth2 credential in n8n |

#### 3. Configure Google Sheets
- In the **Google Sheets** node, set your Google Sheet document ID
- Ensure the sheet has a tab named `Sheet1`
- Add the following column headers in row 1:
  ```
  Date | TikTok Username | Display Name | Video Description | Video URL | Thumbnail URL | AI Caption (What Is Visible) | Likes | Views | Video Created At
  ```

#### 4. Customize Search Keywords *(Optional)*
In the **Scrape TikTok (RapidAPI)** node, modify:
- `keyword`: Change `"bank duty pakistan"` to any bank/finance related term
- `region`: Change `"pk"` to another country code (e.g., `"us"`, `"gb"`)

#### 5. Adjust Rate Limiting *(Optional)*
- **Limit node**: Change `maxItems` from `5` to a higher number if needed
- **Groq Vision AI node**: `batchSize: 1` with `batchInterval: 8000ms` (8 sec delay) prevents rate-limit errors — adjust as needed

---

## 🛡️ Ethical Usage & Responsible Disclosure

This tool is designed for **cybersecurity research and responsible disclosure** purposes only.

- ✅ Use findings to notify affected banks/individuals through proper channels
- ✅ Report to the relevant bank's security team or CERT-PK
- ❌ Do not use this tool for surveillance, harassment, or unauthorized data collection
- ❌ Do not publicly share or distribute any detected PII

---

## 📋 Rate Limits & Reliability

| Service | Limit | Handling Strategy |
|---------|-------|-------------------|
| RapidAPI TikTok API | Varies by plan | Cursor-based pagination, limited to 5 items/run |
| Groq API | ~30 req/min (free tier) | `batchInterval: 8000ms`, retry on fail (3 retries, 3s delay) |
| Google Sheets API | 300 req/min | Single append per matched record |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|---------|
| `No items returned from TikTok` | Check your RapidAPI key and subscription plan for TikTok API23 |
| `Groq API 429 Too Many Requests` | Increase `batchInterval` in the Groq Vision AI node options |
| `Google Sheets OAuth error` | Re-authenticate the Google Sheets credential in n8n settings |
| `AI always returns "No leak"` | Verify the thumbnail URL is publicly accessible (not expired) |
| `Filter passes everything` | Check the regex pattern — ensure case-insensitivity is enabled |

---

## 🗂️ Project Structure

```
n8n-workflows/
├── Bank PII Leak Detector (TikTok).json   ← n8n workflow (API keys redacted)
└── README.md                               ← This documentation
```

---

## 🔗 Related Technologies

- [n8n Documentation](https://docs.n8n.io/)
- [Groq API Docs](https://console.groq.com/docs/openai)
- [TikTok API23 on RapidAPI](https://rapidapi.com/tikwm-tikwm-default/api/tiktok-api23)
- [LLaMA 4 Scout Model Card](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)

---

## 👨‍💻 Author

**Hassan Ali**  
AI & Automation Engineer | Cybersecurity Researcher  
[GitHub: hassanali241](https://github.com/hassanali241)

---

*Built with ❤️ using n8n — the fair-code workflow automation platform.*
