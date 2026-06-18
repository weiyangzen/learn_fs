<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.h -->
# `sources/test-tools/filebench/cvars/cvar-erlang.h`

Purpose: Private header for the Erlang CVAR module.

Important types/macros: parameter keys `RER_SHAPE` and `RER_RATE`, defaults `RER_SHAPE_DEFAULT` and `RER_RATE_DEFAULT`, `VERSION`, `USAGE_LEN`, global `usage`, and `handle_t` containing `mt_state state`, `int shape`, and `double rate`.

Control flow: no executable flow; it supplies compile-time constants and the handle layout consumed by `cvar-erlang.c`.

State and persistence: `handle_t` is copied into Filebench-managed memory and persists RNG state across generated values. `usage` caches the generated usage string for the module process.

Dependencies and integration: includes `mtwist/mtwist.h`; must match `cvar-erlang.c` and `randistrs` expectations for `rds_erlang`.

Risks: `usage` is a non-static definition in a header; safe only because each plugin builds one distribution source, but it would cause duplicate symbols if multiple CVAR headers were linked into one object set. `rate` naming may not match `rds_erlang` mean semantics.

Test signals: compile the module and verify `cvar_usage()` prints defaults and example matching these macros.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.h -->
