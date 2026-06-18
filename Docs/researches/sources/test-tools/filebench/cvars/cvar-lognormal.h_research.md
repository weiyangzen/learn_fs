<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.h -->
# `sources/test-tools/filebench/cvars/cvar-lognormal.h`

Purpose: Private declarations for the lognormal CVAR module.

Important types/macros: `RLN_SHAPE`, `RLN_SCALE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state`, `shape`, and `scale`.

Control flow: no executable code; provides compile-time names/defaults and shared memory layout.

State and persistence: `handle_t` persists PRNG and distribution parameters. `usage` caches help output per module.

Dependencies and integration: includes `mtwist/mtwist.h`; used by `cvar-lognormal.c`.

Risks: include guard closing comment says `_RAND_NORMAL_H`, which is misleading though harmless. Header-level global `usage` is fragile outside one-source-per-plugin builds.

Test signals: compile warnings should catch guard/comment mismatch only if style checks exist; runtime usage should show shape and scale defaults.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.h -->
