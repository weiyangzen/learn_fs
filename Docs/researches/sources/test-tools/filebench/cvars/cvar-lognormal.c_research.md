<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.c -->
# `sources/test-tools/filebench/cvars/cvar-lognormal.c`

Purpose: Filebench CVAR plugin returning lognormal random values.

Important APIs/functions: standard CVAR entry points; uses tokenizer helpers, `mts_goodseed`, `mts_mark_initialized`, and `rds_lognormal`.

Control flow: allocation parses `shape` and `scale`, defaults both to `1.0`, rejects negative values, rejects unknown tokens, seeds MT state, allocates/copies the handle, and frees token state. Sampling calls `rds_lognormal(&h->state, h->shape, h->scale)`.

State and persistence: `handle_t` stores MT state, shape, and scale in Filebench-managed memory. Revalidation marks MT state initialized after process-local reload.

Dependencies and integration: built as `libcvar-lognormal.la`; depends on `randistrs` for distribution math and `cvar-lognormal.h` for layout/defaults.

Risks: validation text says non-zero positive but zero is accepted. `atof` masks invalid strings as zero. Null pointer errors use `cvar_trace`, so they disappear in non-DEBUG builds.

Test signals: default and explicit shape/scale sampling, negative parameter rejection, zero handling, unsupported token rejection, and revalidation before sampling reused handles.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-lognormal.c -->
