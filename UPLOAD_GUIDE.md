# Nova Debt AI — YouTube Upload Guide

## 📺 Channel Setup

### Recommended Channel Name
**Nova Debt AI** — clean, searchable, matches the brand.

Alternative options:
- Nova Debt Helper
- Visionary Consultant (matches website)

### Channel Branding
- **Profile picture:** Use `/root/sites/visionary-consultant/brand/nova-icon.svg` (convert to PNG first, 800x800)
- **Banner:** Create a banner with "Nova Debt AI — Your Free AI Debt Coach" on the dark navy background with teal accent
- **Description:** "Free AI debt coach that builds your personalized payoff plan in seconds. Debt tips, money hacks, and motivation to get you to debt freedom. Try it free → visionary-consultant.pages.dev"
- **Links:** Add visionary-consultant.pages.dev as the website

### Channel Settings
- **Category:** Education
- **Language:** English
- **Country:** United States
- **Tags:** debt, personal finance, debt free, credit cards, budgeting, investing, money tips

---

## 📤 How to Upload Videos to YouTube

### Method 1: Manual Upload (Start Here)

1. Go to **https://studio.youtube.com**
2. Click **"Create" → "Upload videos"**
3. Drag & drop the MP4 file from `/root/sites/video-generator/output/`
4. Fill in:
   - **Title:** Use the title from the caption file (e.g., `The Minimum Payment Trap Explained`)
   - **Description:** Copy from the `_caption.txt` file in the output folder
   - **Tags:** debt, personalfinance, debtfree, creditcards, moneytips
5. **Important settings:**
   - ✅ Make it a **Short** (videos under 60s auto-classify as Shorts)
   - ✅ Set as **Public** (for maximum reach)
   - ✅ Enable **captions** (auto-generated is fine)
   - ✅ Set **audience:** "Not made for kids"
   - ✅ **Allow remixing** (good for reach)
6. Click **Publish**

### Method 2: Bulk Upload
1. From YouTube Studio, you can upload multiple videos at once
2. Schedule them for different days/times using the **Schedule** option
3. Recommended: Upload 7 videos at a time, schedule one per day at 12pm MT

---

## 🔑 Getting a YouTube API Key (For Automated Uploads Later)

To automate uploads via the script, you need YouTube Data API v3 credentials:

### Step-by-Step

1. Go to **https://console.cloud.google.com/**
2. Create a new project (or select existing) — name it "Nova Debt AI"
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click **Enable**
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click **"Create Credentials" → "OAuth client ID"**
   - Application type: **Desktop app**
   - Name: "Nova Video Uploader"
   - Download the JSON credentials file
5. Get your refresh token:
   - Run the auth flow once to authorize the app
   - Save the refresh token for automated uploads

### What You'll Need for the Upload Script
- `client_id` — from the OAuth credentials JSON
- `client_secret` — from the OAuth credentials JSON
- `refresh_token` — obtained after first authorization

### Scope Required
- `https://www.googleapis.com/auth/youtube.upload`

### Quota
- YouTube API gives **10,000 units/day** by default
- Each upload costs ~1,600 units → you can upload ~6 videos/day
- Request a quota increase if needed: https://support.google.com/youtube/contact/yt_api_form

---

## 📋 Upload Checklist (Per Video)

- [ ] Video is MP4, 9:16 vertical, under 60 seconds
- [ ] Title is catchy and under 100 characters
- [ ] Description includes hashtags and CTA with link
- [ ] Thumbnail is clear (YouTube auto-generates for Shorts, but check it)
- [ ] Set as Public
- [ ] Audience: "Not made for kids"
- [ ] Allow remixing enabled
- [ ] Post at 12pm MT for best Shorts reach

---

## 🎯 SEO Tips for YouTube Shorts

1. **First 3 seconds matter** — the hook must grab attention immediately
2. **Use keywords in the title** — "credit card debt", "pay off debt", "money tips"
3. **Hashtags in description** — not in title
4. **Consistent posting** — 1/day minimum for algorithm favor
5. **Engage with comments** — reply within 1 hour of posting
6. **Pin a comment** with the CTA link to Nova

---

## 🔗 Important Links

- **Website:** https://visionary-consultant.pages.dev
- **Debt Chat:** https://visionary-consultant.pages.dev/debt.html
- **YouTube Studio:** https://studio.youtube.com
- **Google Cloud Console:** https://console.cloud.google.com
- **Nova Brand Assets:** /root/sites/visionary-consultant/brand/
