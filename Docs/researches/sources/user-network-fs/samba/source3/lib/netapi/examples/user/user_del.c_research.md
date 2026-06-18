# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_del.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_del.c

Purpose: Demonstrates deleting a user account with `NetUserDel()`.

Important APIs/types/functions: Calls `NetUserDel(hostname, username)`.

Control flow: Parses hostname and username, calls the delete API, prints error information, and frees libnetapi/popt resources.

State and persistence behavior: Removes persistent user account state from the target server/domain.

Dependencies and integration points: Cleanup counterpart for `user_add`.

Risks: Destructive and lacks confirmation. Does not inspect profile/home directories or group references.

Test signals: Delete a disposable user and verify `user_getinfo` fails afterward.
