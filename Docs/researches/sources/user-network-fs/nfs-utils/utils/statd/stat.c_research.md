## sources/user-network-fs/nfs-utils/utils/statd/stat.c

Purpose: Implements the NSM `SM_STAT` procedure.

Important APIs/types/functions: `sm_stat_1_svc` resolves the requested monitor name via `statd_canonical_name` and returns `STAT_SUCC` or `STAT_FAIL` plus local `MY_STATE`.

Control flow: On request, log caller name, attempt canonical resolution, set result status accordingly, free the resolved name, set state, and return a static response.

State and persistence: Reads local NSM state from global `MY_STATE`; no persistent mutation.

Dependencies and integration: Used by RPC dispatch; relies on DNS/canonicalization helper.

Risks and test signals: Resolver availability controls success and can block. Tests should cover resolvable host, unresolved host, numeric address, and returned state.
