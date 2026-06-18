<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c

## Purpose
This file implements the passdb/SAMR-backed winbind backend method tables for local SAM, BUILTIN, and internal RPC access. It bridges high-level `winbindd_methods` operations to cached internal SAMR/LSA pipes and the reusable helpers in `winbindd_rpc.c`.

## Important APIs, Types, And Functions
Connection setup is handled by `open_internal_samr_conn()`, `open_internal_lsa_conn()`, and `open_cached_internal_pipe_conn()`, with cached state in `struct winbind_internal_pipes`. Backend operations include `sam_enum_dom_groups`, `sam_query_user_list`, `sam_trusted_domains`, `sam_enum_local_groups`, `sam_name_to_sid`, `sam_sid_to_name`, `sam_rids_to_names`, `sam_lockout_policy`, `sam_password_policy`, `sam_lookup_usergroups`, `sam_lookup_useraliases`, `sam_lookup_groupmem`, and `sam_lookup_aliasmem`. The exported method tables are `builtin_passdb_methods` and `sam_passdb_methods`.

## Control Flow
The cached pipe opener lazily creates internal SAMR and LSA pipes, opens domain/policy handles, and installs a five-second idle timer that frees the cached pipe bundle. Most SAM operations call `open_cached_internal_pipe_conn()`, invoke a `rpc_*` helper or generated SAMR call, and retry once if `reset_connection_on_error()` sees a timeout, device error, or disconnected binding handle. Name/SID conversion has special local handling for Unix users/groups, well-known SIDs, the domain SID itself, and optional name normalization before falling back to SAMR `LookupNames` or `LookupRids`.

## State And Persistence Behavior
State is cached in `domain->backend_data.samr_pipes` and expires through a tevent timer. Domain method tables themselves are static. The code reads passdb, Unix passwd/group databases, machine SID state, and SAMR/LSA policies, but does not persist new records. Name normalization may consult alias caches and mark domains offline when alias lookup reports DC unavailability.

## Dependencies And Integration Points
It depends on internal RPC pipe support, generated SAMR/LSA stubs, passdb and Unix SID helpers, global event contexts, and `winbindd_rpc.h`. It integrates into winbind backend dispatch for the local SAM and BUILTIN domains and is used by higher-level NSS, SID/name lookup, group membership, and policy calls.

## Risks And Test Signals
Risks include cached policy handles becoming stale, retry logic hiding transport failures but not semantic errors, subtle output-pointer ownership through temporary talloc frames, and compatibility expectations for Unix pseudo-domains and well-known SIDs. Build-sensitive risk exists around exact function signatures and generated SAMR calls. Strong test signals are local SAM SID/name round trips, BUILTIN alias expansion, password and lockout policy queries, group membership lookups, and forced pipe disconnect tests that verify one retry and cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_samr.c -->
