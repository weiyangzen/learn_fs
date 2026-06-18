# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_del.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_del.c

Purpose: Demonstrates deleting a local group with `NetLocalGroupDel()`.

Important APIs/types/functions: Calls `NetLocalGroupDel(hostname, groupname)`.

Control flow: Parses hostname and group name, calls the delete API, prints context error details on failure, and frees context/popt.

State and persistence behavior: Removes local group state from the target server.

Dependencies and integration points: Cleanup counterpart to local group creation examples.

Risks: Destructive and lacks confirmation. Existing ACL references are outside the sample's scope.

Test signals: Delete a disposable group and confirm `localgroup_getinfo` fails.
