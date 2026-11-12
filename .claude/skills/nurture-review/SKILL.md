---
name: nurture-review
description: Review a Frugal Testing nurture list (an Instantly export of contacts already emailed) and decide, contact by contact, who to email again, who goes to sales, and who to leave out, with a reason for each. Free checks first, paid lookups only after the user's yes, hand review of every company that is not plainly out, personal copy for real software companies, a plain email for the rest, mailbox check, one master workbook per list. Use when the user gives one or more Instantly exports (leads.csv), says nurture, or asks which old contacts to email.
---

# Nurture review

Input: one or more Instantly exports (CSV with `Email`, `Lead Status`, `email_open_count`, `email_reply_count`,
`Campaign Name`, `company_domain`). Output, per list: send files, a rejected file, a HOT file and one master workbook.
**Nothing is ever sent from this repo.** Every rule in CLAUDE.md "Rules that must hold on every run" applies.
Results, real costs and mistakes from the first run (4 lists, 5 Nov 2026) are in `REFERENCE.md` next to this file.

## How to work with the user

- Plain, simple words. Short points or small tables. Real numbers, never "about" when the exact number is known.
- **Add numbers twice before you say them.** On 5 Nov a wrong total (9,996 for 8,996) went to the CEO.
- Say the Apify cost before every paid step and wait for "yes". "Go" alone is not a yes to a price never shown.
- During long runs: an update every 5 minutes (a background `sleep 290` wakes you), and put idle keys to work at once.
- Say plainly what failed and what it cost. Never claim a check you did not run.

## Rules that decide every contact

| Rule | Why |
|---|---|
| **One list, one folder, one master. Never merge lists.** | The user's team uploads each campaign on its own. |
| A company's keep or drop decision may be shared between lists; a contact, file or result never moves between lists. | One company is judged one way. |
| **Overlaps between lists are ignored**, except suppression. | User's decision. |
| **Suppression wins on every list**: an opt-out or bounce found on any list removes that person everywhere. | Found 6 such contacts on 5 Nov. |
| **An invalid address is always rejected**, even if Instantly shows an earlier open. | User's decision, 5 Nov. |
| **Never opened is not a reason to reject.** Valid or opened before = Ready; neither = Hold, still emailed. | User's decision. |
| HOT (replied interested) gets no email: hand to sales. | |
| Competitors (QA or testing services) get nothing and go to `config/suppression.csv`. Testing tool vendors are not buyers. | CLAUDE.md. |
| Earlier replies are marked `replied_before`: the team reads them in Instantly before sending. | Some said no. |
| **Unknown is not negative.** A site that did not load is "cannot write a true line", never "not a fit" in `fit_review`. | CLAUDE.md. |

Outcome per contact: **YES** (dated need, kept) and **NOT NOW / UNSURE KEPT** (real software company) get a personal
email; **UNSURE dropped** gets one plain email in a separate untargeted file; **YES or NOT NOW dropped** is NO, not a
buyer; competitor is NO and suppressed.

## Steps

Run from the repo root. `<run>` = `out/nurture-<name>-<YYYY-MM-DD>`, one per list.

| # | Step | Command | Cost |
|---|---|---|---|
| 0 | Keys and credit (never read `.env`) | `python -m gtm apify-keys` | $0 |
| 1 | Import: HOT, opt-outs, bounces, personal and gov addresses set aside; opt-outs added to suppression | `python -m gtm nurture-import --csv "<export>" --out <run>` | $0 |
| 2 | Free checks: homepage fit, careers pages, job boards, score | `python -m gtm accounts --run <run>` then `gtm packs --run <run>` then `gtm nurture-verdicts --run <run>` | $0 |
| 3 | Free homepage read (title, description, LinkedIn link) | `python -m gtm.nurture_lookup meta --runs <run> <run> ...` | $0 |
| 4 | **Price and the user's yes.** Count UNSURE and contacts, give options (below), wait. | | |
| 5 | LinkedIn page, one try per UNSURE company | `python -m gtm.nurture_lookup linkedin --runs ... --keys 3,4,5,6,7,8 --max-usd <cap>` | $0.004 each |
| 6 | Browser read, only where the free read and LinkedIn both failed | `python -m gtm.nurture_lookup render --runs ... --keys ... --max-usd <cap>` | about $0.01 a page |
| 7 | Mailbox check for every YES, NOT NOW, UNSURE contact | `python -m gtm.nurture_lookup verify --runs ... --keys ... --max-usd <cap>` | $0.00089 each |
| 8 | Review queue: first-pass sort, then read the rest by hand | `python -m gtm.nurture_review queue --run <run>`, read `<run>/review_queue.txt` | $0 |
| 9 | Build: decisions, copy, lint, routing | `python -m gtm.nurture_build --run <run> --all-runs <all runs>` | $0 |
| 10 | Shared config: competitors to suppression, hand drops to `fit_review` | `python -m gtm.nurture_finish --runs <all runs>` | $0 |
| 11 | Master workbook (close it in Excel first) | `python -m gtm.nurture_master --run <run> --csv "<export>" --label "List N" --dest <run>/Nurture_Master_ListN_<date>.xlsx` | $0 |
| 12 | Checks, tests, copy lint, hand-off (below) | `python -m pytest -q`, `python -m gtm lint-copy` | $0 |

Steps 5 to 7 can overlap on different keys; 8 can start on YES and NOT NOW while 5 to 7 run.

### Step 4: options to offer (prices from 5 Nov)

- **A, as list 1 was done:** LinkedIn twice (name, then domain), browser read for every unclear site. About $42 for 3 lists.
- **B (chosen 5 Nov):** LinkedIn once, browser read only where nothing else worked. About $24 for 3 lists, $22.94 actual for 4.
- **C:** mailbox check only. About $5.66 for 3 lists; more companies stay unreadable and get the plain email.

### Steps 5 to 7: keys and batches

- Each batch holds **one list only** and is saved in that list's folder (`seeds/apify/nurture_*_bNNN.json`); finished
  batches are skipped on a rerun, and the Apify client caches by input, so a batch is never paid twice once saved.
- One browser crawl per account at a time (free plans cap memory). A key retires itself when its credit is too low.
- Find idle keys with a small script that calls `GET /actor-runs?status=RUNNING` per key (never print a key).
- Put idle keys to work with a second process: `NURTURE_REVERSE=1` works from the far end of the batch list,
  `NURTURE_START=<n>` starts in the middle. `--max-usd` caps the new spend of each process.

### Step 8: hand review

- `review_queue.txt` lists, per company: verdict (Y, N, U), domain, staff, industry, title, description, LinkedIn text.
  The first pass already set aside plain non-buyers (giants over 1,000 staff, under 20 staff for UNSURE, non-software
  LinkedIn industry, "school / clinic / consultancy" in their own words, no sign of a product). It never touches YES.
- **Keep (K):** sells its own software, app, platform or API (SaaS, fintech, edtech, games, marketplaces, AI products).
  Write `domain|Name|line` into `<run>/review_keep_N.txt`. The line follows "which", from their own words: "runs a ...",
  "builds a ...". No numbers unless on their page; no "free", "buy now", "robust" or other linter words; if the word is
  in the company name, use "your company".
- **Drop:** dev shops, product engineering partners, agencies, staffing, IT services, consulting, integrators, ERP
  partners, training, schools, NGOs, VCs, news, hardware, real estate, banks, telecoms, giants, testing tool vendors.
- **Competitor:** QA or testing services, into `<run>/review_competitors.txt` as `domain|competitor: reason`.
- **YES is read twice.** Is it a buyer (not a service firm or giant)? Is the fact true for them? Drop the claim and
  keep a soft note when it is not (add to `NOT_REALLY_YES` in `gtm/nurture_build.py`): on 5 Nov, Nium (compliance QA,
  not software QA), Wellfound and Gloroots (their job pages list their customers' jobs). Check every YES job link loads.
  Status page incidents never open email 1 (R12).
- When the browser read finishes, copy `review_queue.txt` to `review_queue_read.txt`, rerun the queue and read only
  the new lines.

### Step 12: checks before saying done

For every list: every export email appears once in the master; Ready, Hold, Rejected, Untargeted and HOT tabs equal
their CSV files; no suppressed email or domain and no invalid address in a send file; no blank email body; no dash in
copy; `lint_failures.json` empty. Then `python -m pytest -q` and `python -m gtm lint-copy`. Copy the finished files
to `Downloads/Nurture_Reports_<date>/List N/` and compare each copy with its original.

## Hand-off

Say, per list: Ready, Hold, Untargeted, total to send, Rejected, HOT, opted out, skipped, not a buyer, and that they add
up to the export. Then: real intent (YES) versus good fit versus low intent; how many addresses are confirmed valid
(catch-all and unknown can still bounce); earlier replies to read; HOT to sales; cost; what failed. For a CEO: one
small paragraph, exact numbers, "intent" only for YES. Update `README.md`, `HANDOFF_PROMPT.md` and `REFERENCE.md`.
