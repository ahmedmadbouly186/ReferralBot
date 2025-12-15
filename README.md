# Telegram Giveaways & Referrals Bot

Short elevator pitch

- A lean, production-ready Telegram bot that manages referral-driven giveaways, issues time-limited reward codes, and lets an admin broadcast text or media to all users. Built with Python and Google Sheets to minimize costs and keep administration simple for non-technical teams.

What the project solves (business view)

- Grow a Telegram audience using referrals.
- Reward active referrers automatically and securely.
- Let a single admin send promotions or announcements to all registered users and keep a broadcast log.
- Use Google Sheets as a low-cost, visible datastore so non-technical staff can review users, rewards and logs without a database.

Quick user story (non-technical)

- A person sends /start to the bot and is registered.
- The bot gives each user a referral link they can share.
- When friends join with that referral link the referrer’s count increases.
- When counts hit thresholds (tier 1/2/3) the user can request a 6-digit reward code that expires in 14 days.
- The winner redeems the code; admin is notified to complete the reward.
- Admin can broadcast text or media to everyone; each broadcast is saved to Google Sheets.

Key features

- Referral tracking with per-user referral link.
- Tiered rewards and 6-digit, time-limited reward codes.
- Admin-only broadcast of text and media with delivery logs.
- All data and logs stored in Google Sheets (transparent, editable by client).
- Lightweight and cost-effective (no paid DB hosting).

How it works (simple technical overview)

- Bot: Python + pyTelegramBotAPI (telebot).
- Storage: Google Sheets via gspread and a Google service account (credentials.json).
- Main logic lives in project.py:
  - users worksheet: stores user id, username, first name, referral code and referral count.
  - constants worksheet: small key/value table for bot token, admin id, thresholds and invite settings.
  - reward_codes worksheet: stores generated codes, owner, tier and generation timestamp.
- Admin operations secured by matching Telegram user ID configured in constants.
- Broadcasts create a new log worksheet with status per user and a success/failure summary.

Files of interest

- project.py — Production bot logic (register, referrals, reward codes, broadcasts, media).
- example.py — Extended giveaway/promotion scheduler (useful reference for timed postings).
- requirements.txt — Python dependencies.
- credentials.json — Google service account file (must be kept private).
- README.md — This file.

Required Google Sheets structure (simple)

- Worksheet: users — columns: user_id, username, first_name, referral_code, referral_count
- Worksheet: constants — columns: constant_name, value
  - Required keys (examples):
    - bot_token
    - admin_id
    - chat_to_invite_id
    - time_limit_to_acctept_invitation
    - tire1_limit
    - tire2_limit
    - tire3_limit
- Worksheet: reward_codes — columns: code, user_id, username, tier, generated_at (YYYY-MM-DD HH:MM:SS)

Quick setup (for a non-technical admin, or hand off to a developer)

1. Create Google Sheet with the three worksheets listed above and fill constants with correct values.
2. Put service account credentials.json in project folder and share the Google Sheet with service account email.
3. Install Python 3.9+ and run:
   - pip install -r requirements.txt
4. Start the bot (Windows):
   - python project.py
5. Admin: use the Telegram account with admin_id to run /broadcast and send media with broadcast captions.

What to show in a demo (recommended media)

- Screenshot: the Google Sheet showing users, constants and reward_codes.
- Short screen recording (1–2 minutes) showing:
  1. A new Telegram user sending /start and getting a referral link.
  2. Another user joining via referral link and the referrer’s count increasing in the sheet.
  3. Generating a reward code and redeeming it (admin notification visible).
  4. Admin sending a broadcast message and the log sheet being generated.
- Optional: short clip of sending broadcast media (photo/video) and the delivery log.

Why this demonstrates strong skills

- Business-first solution: uses Google Sheets as a single source of truth so non-technical staff can review data and reduces operational costs.
- Clean, pragmatic engineering: reliable Python solution using mature libraries (telebot, gspread, requests) and simple threading for background tasks.
- Security awareness: secrets reside in credentials.json and the bot token (instructions to keep them private).
- Production thinking: admin checks, error logging and broadcast delivery logs show operational readiness.
- Extensible: architecture allows adding more automated giveaways, scheduled posts or a lightweight web dashboard.

Notes, risks & suggested improvements

- Current storage: Google Sheets — excellent for small projects. For high scale (>10k users) migrate to a database (Postgres / Firebase).
- Keep credentials.json and bot token out of version control.
- Add automated tests and CI for production deployments.
- Add rate-limiting and exponential backoff for very large broadcasts to avoid Telegram limits.

Contact / Handoff notes

- Provide the Google Sheet URL and share it with the service account email.
- Provide the credentials.json file and verify the admin_id in constants.
- If you want, I can produce a 60–120s demo video and 4 annotated screenshots for portfolio use (I’ll need temporary access or recordings).

Appendix: Helpful commands

- Run locally on Windows:
  - python project.py
- Install dependencies:
  - pip install -r requirements.txt
