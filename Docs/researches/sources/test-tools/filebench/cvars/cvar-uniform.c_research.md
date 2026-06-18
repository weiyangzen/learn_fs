<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.c -->
# `sources/test-tools/filebench/cvars/cvar-uniform.c`

Purpose: Filebench CVAR plugin returning floating uniform random values.

Important APIs/functions: standard CVAR entry points; uses `rds_uniform`, token helpers, and MT state functions.

Control flow: allocation parses `lower` and `upper`, defaults to `0.0` and `1.0`, logs if `lower > upper`, checks unsupported tokens, seeds state, allocates/copies handle, and sampling calls `rds_uniform(&h->state, h->lower, h->upper)`.

State and persistence: per-handle MT state plus lower/upper bounds, persisted through Filebench memory. Revalidation marks the state initialized.

Dependencies and integration: built as `libcvar-uniform.la`; depends on `cvar-uniform.h`, `randistrs`, tokenizer, and trace.

Risks: validation logs `lower > upper` but does not `goto out`, so invalid bounds still produce an allocated handle and inverted-range samples. `atof` parsing is weak. Unsupported tokens are rejected after validation.

Test signals: defaults, explicit bounds, inverted bounds expecting allocation failure but currently not failing, unsupported tokens, null output pointer, and repeated sampling.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-uniform.c -->
