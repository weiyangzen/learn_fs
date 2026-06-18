# File Research: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.c

- Purpose: debug-mode runtime tracing for `likely()` and `unlikely()`.
- Build condition: only active under `CCAN_LIKELY_DEBUG`.
- Key behavior: records branch condition, file, line, expectation, hit count, and correct count in a typed hash table.
- APIs implemented: `_likely_trace`, `likely_stats`, and `likely_stats_reset`.
- Dependency: uses CCAN hash and htable typed wrappers.
