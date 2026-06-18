# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_addmembers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_addmembers.c

Purpose: Demonstrates adding members to a local group through `NetLocalGroupAddMembers()`.

Important APIs/types/functions: Supports level 0 SID members (`LOCALGROUP_MEMBERS_INFO_0`) and level 3 domain/name strings (`LOCALGROUP_MEMBERS_INFO_3`). Uses `string_to_sid()` and `NetApiBufferAllocate()`.

Control flow: Parses hostname, group, level, and member list, allocates a structure array, converts or assigns each member, calls the API with entry count, frees buffer, and exits.

State and persistence behavior: Mutates local group membership on the remote server.

Dependencies and integration points: Complements get/set/delete member examples; bridges textual SID parsing into NetAPI structures.

Risks: Level 0 rejects invalid SID strings client-side; level 3 leaves name resolution to the server. Operation is additive and may partially fail server-side.

Test signals: Add SID and domain-name members to a test local group and verify via all `localgroup_getmembers` levels.
