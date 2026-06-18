<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nttoken.c -->
# sources/user-network-fs/samba/source3/lib/util_nttoken.c

## Purpose
`util_nttoken.c` contains small security token helpers moved out of auth code to reduce linker dependencies.

## Important APIs, types, and functions
Public functions are `merge_with_system_token` and `token_sid_in_ace`.

## Control flow
`merge_with_system_token` validates parameters, allocates a new token, adds all SIDs from the input token and the system token uniquely, ORs privilege and rights masks from both, and returns the merged token. Claims are not merged because the system token has none. `token_sid_in_ace` scans token SIDs for equality with an ACE trustee.

## State and persistence behavior
The merge result is talloc-owned by the caller. No global state is changed, though `get_system_token` supplies shared system token data.

## Dependencies and integration points
It depends on Samba security token/SID helpers and is used by access-check paths that need to include system privileges.

## Risks and edge cases
Allocation or SID append failure frees the partial token and returns NTSTATUS. The merge deliberately ignores claims, which is safe only while the system token has no claims.

## Test signals
Tests should cover NULL parameters, duplicate SID suppression, privilege/right mask union, allocation failure handling, and ACE trustee matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_nttoken.c -->
