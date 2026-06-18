<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.c -->
# sources/user-network-fs/samba/source3/registry/reg_util_token.c

Purpose: Creates a minimal synthetic administrator-like security token for local registry access.

Important APIs, types, and functions: Exports `registry_create_admin_token(TALLOC_CTX *mem_ctx, struct security_token **ptoken)`. It allocates `struct security_token`, grants `SEC_PRIV_DISK_OPERATOR`, and adds `global_sid_Builtin_Administrators` to the token SID list.

Control flow: The function rejects a NULL output pointer, allocates a zeroed token, sets the disk-operator privilege bit, appends the builtin administrators SID with `add_sid_to_array()`, then returns the token through `ptoken`. On allocation or SID failure it returns the corresponding `NTSTATUS`.

State and persistence behavior: No module-global state is mutated. The returned token and its SID array are allocated below the caller's talloc context. On error after token allocation, the token is not explicitly freed before returning, so normal frame/context cleanup is expected to reclaim it.

Dependencies and integration points: Depends on Samba security token APIs and well-known SID definitions from `../libcli/security/security.h`. Used by local registry code paths that need enough authority to open or modify protected registry content without a real user token.

Risks: This deliberately fabricates elevated local authority; callers must keep it confined to local registry operations. Error cleanup relies on talloc context lifetime. The token includes disk-operator privilege plus builtin administrators membership but not a complete logon/user identity, so downstream authorization code must not assume it represents a real session.

Test signals: Tests should verify NULL-output rejection, no-memory handling, token privilege presence, administrator SID membership, SID-count updates, and that failed SID insertion does not publish a partial token.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.c -->
