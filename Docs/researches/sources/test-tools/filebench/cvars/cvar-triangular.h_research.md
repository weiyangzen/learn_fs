<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.h -->
# `sources/test-tools/filebench/cvars/cvar-triangular.h`

Purpose: Private definitions for triangular CVAR parameters and state.

Important types/macros: `RT_LOWER`, `RT_UPPER`, `RT_MODE`, defaults, `VERSION`, `USAGE_LEN`, `usage`, and `handle_t` containing `mt_state`, `lower`, `upper`, and `mode`.

Control flow: none; constants drive parse and usage output in `cvar-triangular.c`.

State and persistence: handle persists generator state and distribution bounds/mode.

Dependencies and integration: includes `mtwist/mtwist.h`; tied to `rds_triangular` argument order.

Risks: global `usage` symbol in a header. No compile-time enforcement that default mode lies inside bounds, so source validation is the safeguard.

Test signals: generated usage should list all three defaults and example syntax.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.h -->
