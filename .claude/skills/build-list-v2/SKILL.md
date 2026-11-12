---
name: build-list-v2
description: Build a Frugal Testing lead list the v2 way, low cost and many best leads. One cheap scrape per source with search terms aimed at the strongest signals, one shared pool and one score, a strict best-lead gate, then 4 signal packs with their own pitch; people, copy and emails are paid for gated companies only. Default segment is India (india-product-qa). Use when the user asks for build-list-v2, a v2 list, best or strongest leads at low cost, or a list for India.
---

# Build list v2

Goals, in this order: **low cost, best leads, strongest leads, many leads.** Every rule in CLAUDE.md "Rules that
must hold on every run" still applies.

Input: a segment slug (default `india-product-qa`; any `config/icp/<slug>.yaml` with a `best_leads` block works).
Output: a NEW run folder `out/<slug>-<YYYY-MM-DD>/` with `packs/<pack id>/` inside. Never reuse another run's folder.

**Cost at every step.** Before EVERY step, tell the user in one line what it costs: "$0 (free)" for free steps, the
printed Apify estimate for paid ones. Paid steps print their estimate and stop; say the figure, wait for the user's
yes, then rerun with `--yes`. After each paid step say what it actually used and the running total so far.

| Step | Cost |
|---|---|
| 0 Product Hunt (optional, user's choice) | about $0.90 |
| 1 Seeds (India, 2026-11-04): LinkedIn jobs $0.98, Wellfound $0.38, Naukri $0.48, Instahyre $0.29, Cutshort $0.20, hiring posts $0.24, funding $0.40 (evidence only, usually free) | about $2.97 |
| 1 Website lookup for name-only companies, plus HQ and size for job-board companies | $0.004 each, about $0.40 to $0.60 |
| 2 Free checks and score, 3 gate and packs | $0 |
| 4 Optional deep checks: apps on near misses / leaders | under $1 / $0.008 per profile |
| 5 People | about $0.03 per company (3 profiles x $0.008, plus $0.0055 when the LinkedIn page must be looked up) |
| 5 Posts | about $0.006 per person (3 posts x $0.002) |
| 5 Cards, copy (/research-leads), lint, campaign | $0 |
| 6 Emails + verification | about $0.002 per person |

## 0. Ask about Product Hunt (before anything is spent)

Run folder for everything below: `R=out/<slug>-<today>` (a new folder).
Product Hunt is off by default for India (launches are mostly US and rarely give an HQ). Ask the user, with the price:
"Do you want to scrape Product Hunt launches too? It costs about $0.90 and adds launch signals (`product_launch`,
Pack 1); for India it usually adds few companies." Only on a yes, before step 1:
`python -m gtm collect --icp <slug> --out $R --only product_hunt` (prints the price) -> same with `--yes`.
Step 1 keeps these companies (seeds are merged, nothing is paid twice).

```
1 TARGETED SCRAPE  (one scrape per source, ~$2.60)  LinkedIn jobs (QA titles + contract / first QA hire / AI testing
                                                    terms) · Wellfound · funding (brings companies in only) · help posts
2 ONE POOL, FREE CHECKS, SCORE ONCE                 HQ, size, product company (services / training / staffing firms out)
3 BEST-LEAD GATE + PACKS  (free, gtm packs)         1 buying signal, or 2 different strong signals -> a pack
                                                    everything else that qualified -> packs/backup.csv (no spend)
4 OPTIONAL CHEAP PROMOTION  (deep checks, top N)    near misses in backup can earn their second strong signal
5 PER PACK: PEOPLE -> CARDS -> COPY                 gated companies only; no company left without people silently
6 EMAILS LAST, PER PACK, ON THE USER'S GO           find -> verify -> import_ready.csv per pack
```

| Pack | Decided by | Paid checks |
|---|---|---|
| `ai_new_products` (1) | ai_testing_need, qa_gap_language, product_launch, new_app | none |
| `hiring_crisis` (2) | help_post, contract_qa_role, qa_role_unfilled, qa_hiring_spree, qa_leader_hire | none |
| `velocity_rebuild` (3) | release_push, release_cadence, dev_qa_gap, engineering_expansion, automation_adoption, leader_change | leaders (optional) |
| `public_bugs` (4) | status_incidents, app_regression, x / g2 / trustpilot complaints | apps, x (optional) |

`qa_role_open` and `funding` count toward score and gate but never decide which pack (`config/packs.yaml`
`base_signals`). One company, one pack, one sequence.

## 1. Targeted scrape (paid, about $2.60 for India)

Same run folder `$R` as step 0.
`python -m gtm run --icp <slug> --out $R` prints the seed price. After the yes: same command with `--yes`.
That `--yes` also approves the website lookup for companies that came by name only (mostly funding rounds, about
$0.004 each, roughly $0.50 to $1), so say both figures before asking.

The search terms already aim at strong signals (segment `seeds.linkedin_jobs.keywords`): contract QA, first or
founding QA engineer, Head of QA, AI QA and LLM testing, next to the usual QA titles. Do not widen them on your own.

## 2. Read the pool (free)

Read `$R/icp_report.md`. Tell the user: companies, removed by HQ / size / fit (and how many `fit:unknown`), with a
why-now signal, qualified, tier A, top signals. If a removal reason looks wrong for the market (for example Indian
product companies removed as `not_fit`), show 3 examples and suggest one keyword change before going on.

Help posts: check `seeds/help_posts_unmatched.csv` and the kept posts exactly as in `/build-list` step 2
(`config/help_post_review.csv`, then `python -m gtm accounts --run $R`).

## 3. Gate and packs (free)

`python -m gtm packs --run $R`. It writes `packs/assignments.csv` (each company's pack and why it is a best lead),
`packs/packs_report.md`, `packs/backup.csv`, `packs/unassigned.csv`, one folder per pack, and the price of each
pack's paid checks.

Tell the user: qualified, best leads (passed the gate), companies per pack, backup count, top 5 names per pack with
their reason. If the gate passes fewer than about 25 companies, say so and offer step 4 or a bigger scrape (each extra
1,000 LinkedIn job items is about $0.70: raise `seeds.linkedin_jobs.max_items`, rerun collect into the same folder,
then `gtm accounts` and `gtm packs`). Never move a company by hand and never loosen `best_leads` without the user.

## 4. Optional: promote near misses cheaply (paid, small)

Companies in `backup.csv` with ONE strong signal are one signal away from the gate. App reviews are the cheapest way to
find the second one (and they feed Pack 4):

- `python -m gtm deep --run $R --pack backup --only apps --top 40` (prints the price; usually well under $1).
- Pack 3 new leaders only if the user wants them: `python -m gtm deep --run $R --pack velocity_rebuild --only leaders`
  ($0.008 per profile; the dearest check).
- Skip G2 and Trustpilot unless the user asks: few Indian products have those reviews.

Deep checks always run on the MAIN run (never inside a pack folder). Afterwards: `python -m gtm packs --run $R`
again and report who was promoted. If it warns that a company with people or copy moved pack, remove that company's
rows from the old pack folder before emails.

## 5. Per pack: people, research, copy (no emails yet)

For each pack the user wants worked, `P=$R/packs/<pack id>`:

1. `python -m gtm people --run $P` (paid; prints the price). Help-post authors and new leaders come first.
   Then read the printed WARNING and `$P/people_missing.csv`. Never carry on as if those companies were covered:
   `python -m gtm people --run $P --only-missing --yes` once, then Apollo (`--apollo-json <file>`) for the rest if the
   user has it. Report companies with people / without.
2. `python -m gtm shortlist --run $P --top 200` (max 2 per company, signal-named people and QA / engineering leaders first).
3. `python -m gtm posts --run $P` (paid, about $0.002 per person), then `python -m gtm cards --run $P` (free; each card
   carries the pack's angle and preferred claims).
4. Copy: `/research-leads` on `$P`, or `python -m gtm write --run $P`. Follow `pack.angle`, prefer `pack.claims`; every
   rule wins over the angle. Then `python -m gtm lint-personal --run $P`.
5. `python -m gtm campaign --run $P`; show the user `campaign_review.md`.

Pack 4 copy: R12 holds. Email 1 and the LinkedIn note open on a neutral fact (release, launch, hire, their own post),
never on complaints; complaints may open email 2 (`hook_2`) as what the reviews report. No neutral fact, no copy.

Pitches: only claims in `config/claims.yaml`. No "zero bugs", no "48 hour" promise. Never fill in `approved_by`.
For India, `named_clients` (CRED, Paytm ...) is a strong claim; `sarvam_reference` and `ai_agents_delivery` need a
person's sign-off first.

## 6. Emails, last, per pack, on the user's go

Per pack, exactly as `/build-list` step 5: `gtm emails --run $P` -> `--yes`, `gtm verify-emails --run $P` -> `--yes`
(or `--apollo-status`; say so in the hand-off), `gtm finalize --run $P`, `gtm sheet --run $P`, `gtm qa --run $P`.
One `import_ready.csv` per pack = one campaign per pack in the sequencer.

## 7. Report back

Per pack: best leads, tier A, the signals behind them, people found / missing, rows with researched copy, emails found,
verified. Plus backup and unassigned counts, total Apify spend and **cost per ready lead**. Point to each pack's
`import_ready.csv` and workbook. Offer the backup list as a later, lighter campaign ("cover the testing while you
hire"), paid only on the user's yes. Never import, upload or send anything.
