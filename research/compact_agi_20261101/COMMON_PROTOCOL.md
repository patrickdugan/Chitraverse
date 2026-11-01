# Shared continuation and output protocol

This packet prepares eight independent future research sessions. It does not start them. Current state is **BLOCKED_NOT_LAUNCHED**: no xHigh session, chat, experiment, training run, paid call, or result exists. A prompt is a launch brief, not evidence of execution.

## Before substantive work
1. Confirm the exact repository/brief, session owner, and that the prior assistant response is fully visible through its final text. Never infer completion from a partial answer or activity indicator.
2. Verify the session actually exposes the requested xHigh reasoning setting. If not, stop and report the exact available setting; do not relabel another mode.
3. Read each assigned source in full from its latest version. Record version/date and exact section or equation used. Abstract-only coverage is insufficient for theorem-level claims.
4. Record the agreed time, token, compute, and API budget before work. Separate offline source acquisition from runtime/adaptation/search costs. No hidden frontier-model fallback or unapproved training/GPU/checkpoint/API spend.
5. Keep sealed acceptance answers private and outside this repository. Do not commit wholesale copyrighted sources.

## Evidence and claims
Use sources.jsonl records with url, version, access_date, retrieval_scope (fulltext, abstract_only, or metadata_only), sections_read, and source hash when lawfully available. In claims.md, label each statement **source**, **derived**, or **conjecture**, give its source/section or derivation, and state a falsifying test. Preserve negative findings. Financial-to-AI links remain hypotheses unless a valid mapping and evidence are supplied.

## Required deliverables
Produce README.md, sources.jsonl, claims.md, SPEC.md, EVALUATION.md, HANDOFF.md, and append-only receipts.jsonl. The receipt schema must capture verified chat/session ID, model, reasoning setting, prompt ID, source/version and SHA, actual completion state, artifact hashes, and pushed commit SHA. Unknown values remain null; never invent identifiers or claim success without observable evidence. Hashes attest bytes, not correctness.

## Continuation tail
At the end of each response, read the complete latest response including its final text and verify current idle/owner state. Then select exactly one unmet completion criterion and address it with new evidence, a counterexample, or a falsifiable check. Stop after that single bounded action. Never issue a blind “go on”, repeat an uncertain send, or treat silence as completion. If state or delivery is uncertain, inspect before acting. If blocked, record the blocker and stop.
