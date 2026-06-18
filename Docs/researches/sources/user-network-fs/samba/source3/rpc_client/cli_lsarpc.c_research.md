<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c -->
# sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c

Purpose: Provides higher-level client helpers for Local Security Authority RPC operations: opening LSA policy handles and translating between SIDs and account names.

Important APIs, types, and functions: Exports `dcerpc_lsa_open_policy()`, `rpccli_lsa_open_policy()`, `dcerpc_lsa_open_policy2()`, `dcerpc_lsa_open_policy3()`, `dcerpc_lsa_open_policy_fallback()`, `dcerpc_lsa_lookup_sids_generic()`, `dcerpc_lsa_lookup_sids()`, `rpccli_lsa_lookup_sids()`, `dcerpc_lsa_lookup_sids3()`, `dcerpc_lsa_lookup_names_generic()`, `dcerpc_lsa_lookup_names()`, `rpccli_lsa_lookup_names()`, and `dcerpc_lsa_lookup_names4()`. Internal `dcerpc_lsa_lookup_sids_noalloc()` performs one RPC translation hunk into caller-provided arrays.

Control flow: Open-policy helpers prepare `lsa_ObjectAttribute` and optional `lsa_QosInfo`, then call generated NDR client stubs. The fallback helper tries OpenPolicy3, falls back to OpenPolicy2 on missing procedure or after reopening unauthenticated on access denied. SID lookup allocates output arrays, processes inputs in hunks of 1000 SIDs, calls either LookupSids or LookupSids3, maps translated names through returned domain indexes, and combines hunk statuses into OK, some-unmapped, or none-mapped. Name lookup converts strings to `lsa_String`, calls LookupNames or LookupNames4, validates returned counts and domain indexes, builds SIDs by combining domain SID plus RID where needed, and optionally returns domain names.

State and persistence behavior: No module-global state. All returned arrays and strings are talloc-owned by the caller's memory context. Policy handles are server-side state represented by output `policy_handle` values. The fallback path can mutate the RPC pipe authentication state by reopening a named pipe without auth.

Dependencies and integration points: Depends on generated `ndr_lsa_c` stubs, `rpc_pipe_client`, `cli_pipe`, LSA initialization helpers, SID helpers, and `lsa.h` status macros. It bridges low-level generated RPC calls to Samba callers that want simpler NTSTATUS-returning lookup APIs.

Risks: Correctness depends on strict validation of server-returned counts and domain indexes; this code handles several invalid response cases. The hunking logic uses pointer arithmetic across output arrays and must keep arrays sized to `num_sids`. `dom_names` returned by name lookup point into RPC response memory under `mem_ctx`, not newly duplicated strings. The fallback from policy3 access denied to noauth policy2 changes security posture and should remain intentional.

Test signals: Tests should cover policy open with and without QoS, policy3 fallback cases, hunking over 1000 SIDs, none/some/all mapped status composition, invalid network responses with short arrays or bad domain indexes, LookupSids3/LookupNames4 variants, zero inputs, and ownership of returned names/domains/SIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/rpc_client/cli_lsarpc.c -->
