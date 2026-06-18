<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.c -->
# `sources/test-tools/filebench/cvars/cvar-exponential.c`

Purpose: Filebench CVAR plugin returning exponentially distributed random values.

Important APIs/functions: CVAR entry points `cvar_alloc_handle`, `cvar_revalidate_handle`, `cvar_next_value`, `cvar_free_handle`, `cvar_usage`, and `cvar_version`. Uses token helpers, `mts_goodseed`, `mts_mark_initialized`, and `rds_exponential`.

Control flow: allocation parses optional `mean`, defaults to `1.0`, clamps negative means to zero, rejects unused tokens, seeds MT state, allocates the handle through Filebench, and copies it. Sampling validates pointers and returns `rds_exponential(&h->state, h->mean)`.

State and persistence: `handle_t` stores `mt_state` and `mean`; revalidation marks the state initialized when reused in another process. Static `usage` caches formatted help.

Dependencies and integration: depends on `mtwist`, `randistrs`, the CVAR ABI, trace macros, and tokenizer. Built as `libcvar-exponential.la`.

Risks: negative mean silently becomes zero; this may hide bad workload parameters. `atof` accepts malformed strings as zero. `cvar_usage()` mentions only key/value assignment and omits the parameter delimiter because there is one parameter.

Test signals: default allocation, explicit `mean`, negative mean behavior, unsupported parameter handling, null handle/value checks, and sample values from `rds_exponential`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/cvar-exponential.c -->
