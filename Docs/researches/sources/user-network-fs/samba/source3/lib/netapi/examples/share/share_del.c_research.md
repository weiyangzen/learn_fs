# sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_del.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_del.c

Purpose: Demonstrates deleting a share with `NetShareDel()`.

Important APIs/types/functions: Calls `NetShareDel(hostname, netname, reserved)` with reserved value zero.

Control flow: Parses hostname and share name, calls the API, prints error string on failure, and releases resources.

State and persistence behavior: Removes remote share configuration.

Dependencies and integration points: Cleanup counterpart to `share_add`.

Risks: Destructive and lacks confirmation. Existing client connections and filesystem contents are outside the sample's scope.

Test signals: Delete a disposable share and verify it no longer appears in `share_enum`.
