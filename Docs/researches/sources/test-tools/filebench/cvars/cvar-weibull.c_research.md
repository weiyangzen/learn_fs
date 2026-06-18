<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.c -->
# `sources/test-tools/filebench/cvars/cvar-weibull.c`

Purpose: Filebench CVAR plugin returning Weibull-distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_weibull`, tokenizer helpers, and MT state management.

Control flow: allocation parses `shape` and `scale`, defaults to `1.0`, rejects negative values, rejects unused tokens, seeds MT state, allocates/copies the handle, and sampling calls `rds_weibull(&h->state, h->shape, h->scale)`.

State and persistence: handle contains MT state and shape/scale. Revalidation marks MT state initialized.

Dependencies and integration: built as `libcvar-weibull.la`; depends on `cvar-weibull.h`, `randistrs`, trace, tokenizer, and `mtwist`.

Risks: zero shape or scale is accepted despite error text saying non-zero positive. Shape error text says integer even though the field is `double`. `atof` lacks strict parsing. Null pointer diagnostics use trace and may compile out.

Test signals: default and explicit sampling, negative value rejection, zero behavior, unsupported parameter handling, and revalidation.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-weibull.c -->
