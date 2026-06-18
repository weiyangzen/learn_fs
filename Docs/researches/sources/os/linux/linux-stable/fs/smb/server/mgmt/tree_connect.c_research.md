# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.c

Read status: complete.

## Purpose
Creates, looks up, and disconnects per-session tree connections to shares.

## Main Responsibilities
- Fetch share configuration and allocate a `ksmbd_tree_connect`.
- Allocate tree IDs from the session IDA.
- Ask userspace IPC to authorize tree connection using session, share, tree, and peer address data.
- Handle share config update requests by refreshing stale cached shares.
- Store connected trees in the session xarray.
- Refcount tree connections and release associated share configs.
- Notify userspace on tree disconnect and session logoff.
- Destroy all tree connections during session logoff.

## Dependencies And Role
Bridges SMB2 TREE_CONNECT/TREE_DISCONNECT behavior with share config cache, sessions, IPC, and counters.

## Risks
Tree ID release, xarray erase, IPC disconnect notification, and refcount release must happen exactly once. Update handling must avoid using stale share config after userspace requests refresh.
