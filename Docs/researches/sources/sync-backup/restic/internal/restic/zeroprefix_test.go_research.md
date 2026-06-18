<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix_test.go -->
# sources/sync-backup/restic/internal/restic/zeroprefix_test.go

## Purpose
Validates and benchmarks `ZeroPrefixLen`.

## Important APIs and Control Flow
`TestZeroPrefixLen` runs table cases for empty input, zero bytes, and mixed byte prefixes; `BenchmarkZeroPrefixLen` measures repeated calls on representative byte slices. Control flow is simple table iteration with exact expected leading-zero-bit counts.

## State, Persistence, Dependencies, and Integration
No persistent state. Tests depend on the exported `restic.ZeroPrefixLen` API from the external test package.

## Risks and Test Signals
The coverage is strong for edge cases and regressions in bit accounting, though it does not tie the helper to higher-level ID-search behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix_test.go -->
