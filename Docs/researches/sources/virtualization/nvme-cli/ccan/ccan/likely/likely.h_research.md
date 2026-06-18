# File Research: sources/virtualization/nvme-cli/ccan/ccan/likely/likely.h

- Purpose: branch prediction macros.
- Normal mode: maps `likely(cond)` and `unlikely(cond)` to `__builtin_expect` when available, otherwise boolean normalization.
- Debug mode: redirects macros through `_likely_trace` with stringified condition, source file, and line.
- Extra debug APIs: `likely_stats` reports worst prediction sites; `likely_stats_reset` frees trace memory.
