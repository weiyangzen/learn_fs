# File Research: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.c

This file manages SMB tree connections between a session and a share.

Main behavior:
- `ksmbd_tree_conn_connect()` gets share config, allocates a tree connect, acquires a tree ID, asks userspace IPC to authorize the connection, handles stale-share update requests, links the user/share to the tree, and stores it in the session xarray.
- Tree connection creation increments KSMBD tree connection counters.
- `ksmbd_tree_conn_lookup()` returns only connected tree connections and takes a refcount.
- `ksmbd_tree_conn_disconnect()` removes the tree from the session xarray, sends userspace disconnect IPC, releases the tree ID, decrements counters, and drops references.
- `ksmbd_tree_conn_session_logoff()` disconnects all trees for a session and destroys the xarray.

The file coordinates share config lifetime, userspace authorization, and per-session tree ID ownership.
