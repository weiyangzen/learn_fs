<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.h -->
# `sources/test-tools/filebench/cvars/cvar-uniform.h`

Purpose: Private definitions for the uniform CVAR module.

Important types/macros: `RU_LOWER`, `RU_UPPER`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state state`, `double lower`, and `double upper`.

Control flow: no executable flow.

State and persistence: handle persists lower/upper bounds and MT state.

Dependencies and integration: includes `mtwist/mtwist.h`; consumed by `cvar-uniform.c`.

Risks: header-defined global `usage`; no local invariant support for lower <= upper beyond source validation.

Test signals: usage output and handle allocation should align with defaults in this header.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.h -->
