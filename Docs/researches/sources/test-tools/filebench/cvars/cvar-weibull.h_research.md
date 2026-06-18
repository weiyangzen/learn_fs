<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.h -->
# `sources/test-tools/filebench/cvars/cvar-weibull.h`

Purpose: Private definitions for the Weibull CVAR module.

Important types/macros: `RW_SHAPE`, `RW_SCALE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with MT state plus shape/scale doubles.

Control flow: none; consumed by source parsing and usage formatting.

State and persistence: per-handle MT state and parameters persist in Filebench memory.

Dependencies and integration: includes `mtwist/mtwist.h`; paired with `cvar-weibull.c` and `rds_weibull`.

Risks: global `usage` in header; no compile-time validation for positive shape/scale.

Test signals: usage string should include shape/scale defaults and delimiter guidance.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.h -->
