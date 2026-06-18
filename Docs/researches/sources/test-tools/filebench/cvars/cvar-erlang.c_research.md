<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.c -->
# `sources/test-tools/filebench/cvars/cvar-erlang.c`

Purpose: Filebench CVAR plugin returning Erlang-distributed random values.

Important APIs/functions: implements mandatory CVAR entry points `cvar_alloc_handle`, `cvar_next_value`, `cvar_free_handle`, plus optional `cvar_revalidate_handle`, `cvar_usage`, and `cvar_version`. It uses `tokenize`, `find_token`, `unused_tokens`, `free_tokens`, `mts_goodseed`, `mts_mark_initialized`, and `rds_erlang`.

Control flow: allocation tokenizes parameters, reads `shape` with `atoi` and `rate` with `atof`, defaults missing values, rejects negative values, rejects unknown tokens, seeds an `mt_state`, allocates a shared handle with Filebench's allocator, and copies stack state into it. `cvar_next_value` validates handle/value pointers and calls `rds_erlang(&h->state, h->shape, h->rate)`.

State and persistence: `handle_t` contains MT state plus `shape` and `rate`; the handle can live in Filebench shared memory. `cvar_revalidate_handle` marks the embedded MT state initialized after process changes.

Dependencies and integration: includes `mtwist/mtwist.h`, `mtwist/randistrs.h`, `cvar.h`, `cvar_trace.h`, `cvar_tokens.h`, and `cvar-erlang.h`. Loaded by Filebench through the symbol contract in `cvar.h`.

Risks: validation accepts zero despite error text saying non-zero positive; `atoi`/`atof` do not detect malformed numeric strings. Parameter name `rate` is passed to `rds_erlang` as the distribution mean per `randistrs` naming, so semantics may be confusing. Null `cvar_parameters` returns NULL via `tokenize`.

Test signals: instantiate with default, explicit `shape:2;rate:1.0`, unsupported parameter, negative values, zero values, and post-fork/shared-memory revalidation; sampling should advance embedded MT state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-erlang.c -->
