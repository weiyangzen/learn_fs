# sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_adduser.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/group/group_adduser.c

Purpose: Demonstrates adding a user account to a global/domain group through `NetGroupAddUser()`.

Important APIs/types/functions: Calls `NetGroupAddUser(hostname, groupname, username)`.

Control flow: Initializes libnetapi, parses common options, requires hostname, group, and username, performs the membership update, reports failures, and releases context.

State and persistence behavior: Mutates remote group membership. No local persistence.

Dependencies and integration points: Complements `group_deluser`, `group_getusers`, and user/group management examples.

Risks: Server-side semantics decide domain resolution and duplicate membership. Requires privileges and valid account/group names.

Test signals: Add a known user to a test group, verify via `group_getusers`, then remove with `group_deluser`.
