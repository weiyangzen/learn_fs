# sources/test-tools/syzkaller/pkg/cover/cover_test.go

Purpose: tests the basic `Cover` set behavior and the per-line range merge logic implemented in `html.go`.

Important APIs/types/functions: `TestMergeDiff` and `TestPerLineCoverage`.

Control flow: `TestMergeDiff` covers nil, empty, full-new, and partially duplicate merges, then sorts `Serialize` output for deterministic comparison. `TestPerLineCoverage` builds covered and uncovered backend ranges spanning single lines, multi-lines, malformed ranges, and overlapping ranges, then compares the produced line chunks.

State and persistence: no persistent state; test slices and maps only.

Dependencies and integration: imports `backend.Range` and `backend.LineEnd` to validate the report-rendering line coverage transformation.

Risks: `TestPerLineCoverage` validates internal chunk shapes, so intentional rendering algorithm changes need expected updates. It does not render HTML, only merge data.

Test signals: catches regressions in both set-diff behavior and the nuanced covered/uncovered/both chunk computation used by HTML and line JSON outputs.
