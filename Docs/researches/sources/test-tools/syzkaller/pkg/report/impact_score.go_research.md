# Research: sources/test-tools/syzkaller/pkg/report/impact_score.go

Purpose: ranks normalized crash titles by estimated security/operational impact. It converts syzkaller crash types into integer scores and explains title-frequency statistics with rank metadata.

Important APIs/types/functions: `impactOrder` is an ordered severity list of `crash.Type`, highest first. `TitlesToImpact(title string, otherTitles ...string) int` maps one or more titles through `crash.TitleToType` and returns the highest rank as `len(impactOrder)-index`, or `-1` for unknown/unranked types. `TitleFreqRank` stores title, observed count, total report count, and rank. `ExplainTitleStat(ts *titleStat)` walks a title-stat trie, de-duplicates titles within each report group, aggregates counts, and sorts by rank, frequency, and title.

Control flow: ranking is table-driven. For multiple titles, the function scans every title and every severity entry, preserving the maximum score. `ExplainTitleStat` visits grouped title paths, aggregates per-title counts only once per visited group, computes ranks, then returns a sorted slice for UI/reporting consumers.

State and persistence: no direct persistence. It consumes `titleStat`, which is serialized by `title_stat.go`, but this file itself only builds transient maps and result slices. The severity table is process-global static policy.

Dependencies and integration points: depends on `pkg/report/crash` for title classification and on the local `titleStat` visitor contract. It integrates with any dashboard or batch tool that wants to prioritize frequent crash titles by impact rather than count alone.

Risks: severity is policy encoded in source order; omitted crash types return `-1` and sink in sorted lists. `crash.TitleToType` normalization changes can silently alter scores. The current nested scan is small enough to be fine, but adding many impact classes would benefit from a precomputed map.

Test signals: unit tests cover unknown titles, unrecognized KASAN titles, a low-priority hang, and multi-title selection of a higher impact KASAN invalid-free over a hang. Additional tests should cover `ExplainTitleStat` sorting ties and per-group de-duplication.
