# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_del.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_del.c

Purpose: Demonstrates deleting a global/domain group with `NetGroupDel()`.

Important APIs/types/functions: Calls `NetGroupDel(hostname, groupname)`.

Control flow: Parses hostname and group name, calls the API, prints error details on failure, and cleans up libnetapi/popt state.

State and persistence behavior: Removes persistent group state from the remote server/domain.

Dependencies and integration points: Cleanup counterpart for `group_add` and setup for group administration tests.

Risks: Destructive operation with minimal confirmation or validation. Existing memberships and ACL references are not inspected.

Test signals: Create a disposable group, delete it, and verify `group_getinfo` fails afterward.
