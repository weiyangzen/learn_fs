# sources/test-tools/lcov/scripts/unreach.pm

Purpose: genhtml/lcov `--unreachable-script` callback that excludes branch and MC/DC coverpoints marked unreachable by source comments.

Important APIs: package `unreach` exposes `new`, `exclude($type, $reader, $testdata, $summary)`, `exclude_branch`, `exclude_cond`, `start`, `save`, `restore`, and `finalize`. Options are `--branch`, `--mcdc`, or neither to use enabled coverage modes.

Control flow and state: constructor validates options and creates regex/count pairs for branch comments `LCOV_UNREACHABLE_BRANCH` and MC/DC comments `LCOV_UNREACHABLE_COND`. `exclude` scans source lines from a reader for matching annotations, parses semicolon-separated exclusion specs, updates summary and per-test maps, and decrements found/hit counters when a coverpoint is newly excluded. `start/save/restore/finalize` reset and aggregate exclusion counts.

Dependencies and integration: depends on `lcovutil` coverage flags and error reporting, `BranchMap` indexes, branch data objects with `getBlock/getElement/set_excluded`, and MC/DC data objects with group/expression APIs.

Risks and test signals: parser error messages mix branch and MC/DC wording. Index validation is delegated to underlying objects and dies on invalid specs. Counter decrements must stay in sync with map layouts. Tests should include branch-only, MC/DC-only, combined comments, invalid ids, multiple testdata maps, and finalize count output.
