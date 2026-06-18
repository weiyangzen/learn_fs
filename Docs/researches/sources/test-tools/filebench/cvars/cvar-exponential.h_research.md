<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.h -->
# `sources/test-tools/filebench/cvars/cvar-exponential.h`

Purpose: Private definitions for the exponential CVAR module.

Important types/macros: `RE_MEAN`, `RE_MEAN_DEFAULT`, `VERSION`, `USAGE_LEN`, global `usage`, and `handle_t` with `mt_state state` and `double mean`.

Control flow: no runtime logic; controls accepted parameter names, defaults, usage formatting, and shared handle shape.

State and persistence: embedded MT state persists per CVAR handle. Static-looking but externally linked `usage` stores help text for the module.

Dependencies and integration: includes `mtwist/mtwist.h`; consumed by `cvar-exponential.c`.

Risks: global `usage` definition in a header would conflict in a combined build. No prototype declarations are provided here; exported function contract comes from `cvar.h`.

Test signals: compile with the source and verify `cvar_usage()` reflects `mean` default `1.0`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.h -->
