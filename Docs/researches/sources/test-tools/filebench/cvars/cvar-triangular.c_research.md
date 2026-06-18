<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.c -->
# `sources/test-tools/filebench/cvars/cvar-triangular.c`

Purpose: Filebench CVAR plugin returning triangular-distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_triangular`, token helpers, and MT state management.

Control flow: allocation parses `lower`, `upper`, and `mode`, defaults to `0.0`, `1.0`, and `0.5`, validates `upper >= lower` and `mode` within bounds, rejects unused tokens, seeds MT state, and allocates/copies the handle. Sampling calls `rds_triangular(&h->state, h->lower, h->upper, h->mode)`.

State and persistence: handle stores MT state and the three distribution parameters. Revalidation marks the embedded state initialized.

Dependencies and integration: built as `libcvar-triangular.la`; depends on `cvar-triangular.h`, tokenizer, trace, `mtwist`, and `randistrs`.

Risks: equal lower/upper is accepted despite message requiring greater-than; that may produce degenerate output. `atof` lacks strict validation. Null pointer logs are emitted with `cvar_log_error` and remain visible.

Test signals: valid defaults, custom bounds/mode, upper-lower inversion, out-of-range mode, equal bounds, unsupported tokens, and sampling reproducibility with a seeded state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-triangular.c -->
