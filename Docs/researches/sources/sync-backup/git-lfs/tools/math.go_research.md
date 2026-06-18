# sources/sync-backup/git-lfs/tools/math.go

Purpose: tiny integer clamp helper.

Important APIs/types/functions: `ClampInt(n, low, high int) int`.

Control flow: returns `min(high, max(low, n))`.

State and persistence: none.

Dependencies and integration points: generic helper for callers needing bounded integer config values.

Risks: assumes `low <= high`; reversed bounds collapse to `high` after nested min/max semantics.

Test signals: `math_test.go` covers below, above, and inside bounds.
