# Compact AGI research campaign packet

**Status: BLOCKED_NOT_LAUNCHED.** This is repository preparation only. It is not a substitute for the eight requested ChatGPT xHigh research sessions. The parent verified that ChatGPT controls cannot establish xHigh or reliably read full answer tails, so no session is launched and no research result is claimed.

## Scope

The motivating hypothesis is a skill-of-skills system a 27B controller can use to route bounded tasks to smaller learners, improve them against independent evaluations, and possibly use routed adapters or decomposed VPD on larger models. “Compactified AGI” is a research aspiration, not an established result or benchmark claim.

The eight briefs isolate theory, reward-to-skill protocols, budget scheduling, specialist routing, proposal selection, evaluation integrity, feedback stability, and transfer across environments. Every cross-domain translation is a hypothesis until its assumptions and evidence are checked.

## Source and repository boundaries

Chitraverse main at f89bc19267cf5d7d1ee99af5da4f2293647e34ad reports 15 writing URLs, 12 authored/linked papers, 14 appearance source URLs (11 publisher-confirmed), zero stored writing/paper text, zero transcript text, and zero tweet records. These are coverage counts, not completeness claims. This packet records source URLs and metadata only; assigned future sessions must read each assigned full paper before theorem claims. Do not put full copyrighted papers, sealed test answers, private transcripts, API keys, or private user data here. The existing private/ and .cache/ ignore rules are left untouched.

No live trading, finance, paid inference, external messaging, training, GPU work, or deployment is authorized by these prompts. No benchmark success alone establishes AGI.

## Eight-thread dependency map

| ID | Track | Source dependency | Produces |
|---|---|---|---|
| 01_bars_theory | BARS theory audit | https://arxiv.org/abs/2504.09777 | bounded research specification and falsifiable checks |
| 02_reward_to_skill | Reward to skill protocol | https://arxiv.org/abs/2504.09777 | bounded research specification and falsifiable checks |
| 03_budget_scheduler | Compute budget scheduler | https://arxiv.org/abs/2602.15182 | bounded research specification and falsifiable checks |
| 04_specialist_routing | Specialist routing and composition | https://arxiv.org/abs/2502.02059 | bounded research specification and falsifiable checks |
| 05_solver_selection | Proposal and solver selection | https://arxiv.org/abs/2403.02525; https://arxiv.org/abs/2301.12532 | bounded research specification and falsifiable checks |
| 06_evaluation_integrity | Evaluation integrity and provenance | https://arxiv.org/abs/2509.18338; https://arxiv.org/abs/2003.10001 | bounded research specification and falsifiable checks |
| 07_feedback_stability | Feedback stability and manipulation | https://arxiv.org/abs/2307.13139; https://arxiv.org/abs/2309.14201 | bounded research specification and falsifiable checks |
| 08_transfer_worlds | Transfer across small worlds | https://arxiv.org/abs/1904.12924 | bounded research specification and falsifiable checks |

Tracks 01–08 are separate work folders and require independent session identity and receipts. Tracks 01 and 02 share BARS but answer distinct theory and protocol questions. Track 03 may supply a conjectural budget-allocation model to compare with 02/05; it must not silently become a theorem. Track 04 frames component types used by 02/05. Track 06 sets provenance and acceptance constraints for every track. Track 07 stress-tests adaptive feedback from 02/03. Track 08 defines transfer evaluation consuming interface proposals from 02/04. Do not merge or cross-edit track outputs without an explicit integration note.

## Files

- INDEX.md: entry points, status, and acceptance contract.
- manifest.json: machine-readable session and track inventory; all runtime identifiers/results are null.
- COMMON_PROTOCOL.md: source, budget, evidence, output, and continuation rules.
- Numbered track folders: self-contained future prompts and concise status.

When sessions are actually run, preserve their real source records, claims, specifications, evaluation plans, handoffs, and append-only receipts in the assigned folder. Missing evidence must remain visibly missing.
