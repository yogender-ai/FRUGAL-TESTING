# Nurture review: first run, 4 lists, 5 Nov 2026

The full record of how the 4 Instantly nurture campaigns were reviewed, what came out, what it cost and what went
wrong. The method is in `SKILL.md`; this file is the evidence and the lessons.

## The 4 lists

| List | Export | Campaign | Folder | Leads |
|---|---|---|---|---|
| 1 | `leads.csv` | Substack_India_BNT_Nurture_Data-WB | `out/nurture-2026-11-04/` | 1,795 |
| 2 | `leads (2).csv` | India_BNT_Nurture_Part-2-WB | `out/nurture-list2-2026-11-05/` | 2,159 |
| 3 | `leads (3).csv` | India_BNT_Nurture_Part-1-WB | `out/nurture-list3-2026-11-05/` | 1,724 |
| 4 | `leads (4).csv` | USA_BNT_Nurture_ WB | `out/nurture-list4-2026-11-05/` | 3,318 |
| | | | **Total** | **8,996** (8,903 unique people; 93 are on two or more lists) |

Copies for the team: a `Nurture_Reports_2026-11-05` folder in Downloads (one folder per list, `READ_ME_FIRST.txt`).

## Results

| Outcome | List 1 | List 2 | List 3 | List 4 | Total |
|---|---|---|---|---|---|
| Ready to import | 317 | 324 | 266 | 325 | 1,232 |
| Hold (never opened, not confirmed; still emailed) | 44 | 19 | 35 | 208 | 306 |
| Untargeted (plain email, separate file) | 480 | 981 | 834 | 1,856 | 4,151 |
| **Total to email** | **841** | **1,324** | **1,135** | **2,389** | **5,689** |
| Rejected (invalid address) | 33 | 54 | 46 | 76 | 209 |
| HOT (to sales) | 3 | 1 | 1 | 0 | 5 |
| Opted out or bounced | 28 | 26 | 7 | 23 | 84 |
| Skipped (personal, gov, university) | 105 | 19 | 51 | 63 | 238 |
| Not a buyer | 785 | 735 | 484 | 767 | 2,771 |
| **Export total** | **1,795** | **2,159** | **1,724** | **3,318** | **8,996** |

What the 5,689 are (contacts; companies in brackets):

| Group | List 1 | List 2 | List 3 | List 4 | Total |
|---|---|---|---|---|---|
| YES: dated need now (real intent) | 8 | 30 | 4 | 7 | **49** (34 companies) |
| NOT NOW and UNSURE kept: real software company, no need seen | 353 | 313 | 297 | 526 | **1,489** |
| Untargeted: low intent | 480 | 981 | 834 | 1,856 | **4,151** |

Mailbox check on the 5,689: valid 2,694; catch-all 1,193 (server accepts every address); unknown 1,802 (no answer).
3,641 opened an earlier email, 2,048 never did (1,527 of those on list 4). 170 replied before and must be read first.

New HOT for sales: 2 contacts (1 on list 2, 1 on list 3); see the HOT tabs in the masters.

**One line for the CEO:** 8,996 leads reviewed, 5,689 to email, and 49 of those show real intent.

## How it was done, in order

1. **List 1 (4 to 5 Nov), older scripts in its folder:** import, free checks, LinkedIn pages for 920 UNSURE twice
   (name, then domain), browser read for about 560 sites, hand review of every YES and NOT NOW (`notnow/review.tsv`),
   copy, mailbox check, then on 5 Nov: hold contacts who opened moved to ready (`move_opened.py`), 566 UNSURE
   companies read by hand (`unsure/review.py`: 70 kept, 495 dropped, 1 competitor), plain email for the dropped ones
   (`unsure/apply.py`), mailbox check for UNSURE (`unsure/verify.py`), later suppressions removed
   (`drop_suppressed.py`), master rebuilt (`build_master.py`). Rerun order: move_opened, unsure/apply, drop_suppressed, build_master.
2. **Lists 2 to 4 (5 Nov), the method in SKILL.md:** import and free checks (YES 67, NOT NOW 1,577, UNSURE 3,450,
   NO 520 companies), free homepage read for 5,094 companies, cost options, option B chosen.
3. LinkedIn: 37 batches on 7 keys in about 6 minutes, 0 failed; 1,906 UNSURE companies matched by domain.
4. Browser read: 716 pages in 19 batches on 6 keys in about 43 minutes, 0 failed; about half the sites returned nothing.
5. Hand review while paid steps ran: 2,325 companies read by hand, 2,769 set aside by the first pass.
   Keepers: list 2 273 companies, list 3 290, list 4 431. Competitors: 8.
6. Mailbox check: 6,358 addresses in 34 batches on keys 1 to 8 (three processes from different ends), none missing.
7. Build, finish, masters, checks. Then the user's rule change (every invalid rejected) and the list 1 UNSURE check.

## Cost (Apify)

| Item | USD |
|---|---|
| List 1, first run (4 to 5 Nov) | about 6.83 |
| LinkedIn company pages, lists 2 to 4 | 11.55 |
| Browser-read homepages, lists 2 to 4 | 7.41 |
| Mailbox checks, lists 2 to 4 and list 1 UNSURE | about 4.0 |
| **Spent on 5 Nov for lists 1 to 4 (keys 1 to 8)** | **22.94** |

Prices: LinkedIn page $0.004; browser page about $0.01; mailbox check $0.00089. Left after the run: $7.65 on keys 1
to 8 (keys 1 to 3 nearly empty), keys 9 and 10 untouched at $5 each.

## Mistakes made, so they are not repeated

| What happened | Fix or rule now |
|---|---|
| Said 9,996 leads; the real total was 8,996. It reached the CEO. | Add every total twice and check the parts add up. |
| A command tried to read variable names from `.env`; it was blocked. | Never read `.env`; use `python -m gtm apify-keys`. |
| Free reads ran one list after another, so list 4 waited. | Run free reads for all lists at once. |
| One Apify bad reply made a running batch look failed; it reran, about $0.30 paid twice. | `gtm/apify.py` now retries a bad status reply. |
| A `sed` edit turned `\s+` into `s+`, so a dash stayed in a YES email. | Edit Python with Python or the Edit tool, then rerun the linter. |
| Long shell heredocs with quotes failed twice. | Write scripts to a file, then run them. |
| An opted-out contact from one list was in another list's send file (6 found). | `gtm/nurture_build.py` and `drop_suppressed.py` check suppression for every contact. |
| Excel kept a master open, so a rebuild silently failed. | Check the file is not locked, never hide build errors, compare counts after. |
| Wrong YES facts (customers' jobs on Wellfound, compliance QA at Nium). | Read every YES fact by hand; `NOT_REALLY_YES`. |
| First-pass drop labels are keyword-based; about 1 in 15 list 1 reasons was worded wrongly. | The keep or drop decision is by hand; say the labels are approximate. |
| Said "invalid and never opened" as one thing; the user was confused. | Invalid (mailbox check) and never opened (Instantly) are separate facts; explain them separately. |

## Known gaps in the master workbooks

- The Summary "Companies" table, the Companies tab and the "Company verdict" column show the **starting** verdicts
  (list 2 YES 36, final 21; list 3 11, final 4; list 4 20, final 7). Contact counts and the YES tab are final.
- List 1's "Fixes and spend" tab shows only the first run's cost (about $6.83).
- YES contacts on lists 2 to 4 had no people research or LinkedIn post cards; their emails open with the careers page
  fact. Engineering role counts were not recounted by hand.
- Companies under 20 staff were set aside by the first pass on UNSURE; they still got the plain email.
