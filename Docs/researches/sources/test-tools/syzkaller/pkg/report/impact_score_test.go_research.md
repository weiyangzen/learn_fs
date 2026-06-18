# Research: sources/test-tools/syzkaller/pkg/report/impact_score_test.go

Purpose: unit-tests the impact-score policy in `impact_score.go`, especially unknown handling and multi-title highest-impact selection.

Important APIs/types/functions: constants `testHangTitle` and `testKASANInvalidFreeTitle` provide stable crash titles. `TestImpactScore` table-tests `TitlesToImpact` for unknown titles, unknown KASAN titles, and a known hang. `TestTitlesToImpact2` checks that a KASAN invalid-free alternative title outranks the primary hang title.

Control flow: each table row calls `TitlesToImpact` and compares the exact expected score. The multi-title test computes the desired KASAN score from `impactOrder` using `slices.Index`, and fails if the returned rank remains at the hang's low score.

State and persistence: no state beyond test constants. The tests are deterministic and do not touch filesystem or external tools.

Dependencies and integration points: imports `testing`, `slices`, and `pkg/report/crash`. It is tightly coupled to `impactOrder`; inserting/removing severity entries can change expected numeric ranks and should update tests intentionally.

Risks: the second test only asserts that the result is not the hang score, not exact equality, so a too-high score could pass. Coverage does not include `ExplainTitleStat`, duplicate titles in one report group, or sorting ties.

Test signals: run with the package tests. A failure usually means crash title classification changed or the severity table was reordered.
