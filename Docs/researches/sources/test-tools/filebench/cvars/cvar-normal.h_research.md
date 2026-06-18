<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.h -->
# `sources/test-tools/filebench/cvars/cvar-normal.h`

Purpose: Private definitions for normal CVAR parameters and handle layout.

Important types/macros: `RN_MEAN`, `RN_SIGMA`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` with `mt_state state`, `double mean`, `double sigma`.

Control flow: no runtime behavior.

State and persistence: handle persists PRNG state and distribution parameters in Filebench memory.

Dependencies and integration: includes `mtwist/mtwist.h` and is consumed by `cvar-normal.c`.

Risks: header defines a global `usage`; fine for one plugin object but unsafe in aggregate builds. It does not encode sigma constraints, leaving validation to source code, which currently does not enforce positivity.

Test signals: compile and `cvar_usage()` should expose default mean `0.0` and sigma `1.0`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.h -->
