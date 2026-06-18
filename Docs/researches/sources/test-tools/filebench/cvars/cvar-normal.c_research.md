<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.c -->
# `sources/test-tools/filebench/cvars/cvar-normal.c`

Purpose: Filebench CVAR plugin returning normally distributed random values.

Important APIs/functions: standard CVAR entry points; uses `rds_normal`, token helpers, and Mersenne Twister seeding/revalidation.

Control flow: allocation reads optional `mean` and `sigma`, defaults to `0.0` and `1.0`, rejects unused tokens, seeds state, allocates the handle, and copies it. Sampling validates inputs and calls `rds_normal(&h->state, h->mean, h->sigma)`.

State and persistence: handle contains embedded MT state plus mean/sigma; `usage` caches formatted help. Revalidation restores MT initialized flag for shared memory handles.

Dependencies and integration: built as `libcvar-normal.la`; depends on `cvar-normal.h`, tokenizer, trace, `mtwist`, and `randistrs`.

Risks: no validation rejects negative sigma, so invalid standard deviations can be passed to `rds_normal`. `atof` gives no parse diagnostics. Null pointer diagnostics use trace macros and may be compiled out.

Test signals: sample defaults, non-default mean/sigma, negative sigma behavior, unsupported parameter rejection, and state revalidation.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-normal.c -->
