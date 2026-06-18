# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_delmembers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_delmembers.c

Purpose: Demonstrates removing local group members with `NetLocalGroupDelMembers()`.

Important APIs/types/functions: Supports member level 0 SID arrays and level 3 domain/name arrays, allocated via `NetApiBufferAllocate()`.

Control flow: Parses hostname/group/level/member args, builds the matching member array, converts SIDs for level 0, calls the delete API, frees the array, and exits.

State and persistence behavior: Mutates remote local group membership.

Dependencies and integration points: Mirrors `localgroup_addmembers` and is verified by `localgroup_getmembers`.

Risks: Weak input validation except SID conversion. Removing wrong members affects local authorization.

Test signals: Add then remove known local group members and enumerate after each step.
