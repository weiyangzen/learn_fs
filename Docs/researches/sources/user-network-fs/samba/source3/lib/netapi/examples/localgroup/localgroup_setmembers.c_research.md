# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setmembers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setmembers.c

Purpose: Demonstrates replacing all local group members through `NetLocalGroupSetMembers()`.

Important APIs/types/functions: Builds `LOCALGROUP_MEMBERS_INFO_0` SID arrays or `_3` domain/name arrays using `NetApiBufferAllocate()`.

Control flow: Parses hostname/group/level/member tokens, allocates and fills the level-specific array, calls `NetLocalGroupSetMembers()`, frees the buffer, and exits.

State and persistence behavior: Replaces remote local group membership state.

Dependencies and integration points: Stronger mutation counterpart to add/delete member examples.

Risks: Destructive replacement can remove administrators or required service accounts. Input is positional and only SID conversion is validated.

Test signals: Apply a known member list to a disposable local group and verify exact membership with `localgroup_getmembers`.
