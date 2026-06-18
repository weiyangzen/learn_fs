# File Research: sources/os/linux/linux/fs/smb/server/mgmt/tree_connect.h

This header defines tree connection state and APIs.

Key contents:
- Tree states: new, connected, disconnected.
- `struct ksmbd_tree_connect` with ID, flags, share config, user, list node, maximal access, POSIX extension flag, refcount, and state.
- `struct ksmbd_tree_conn_status` combining status code and tree pointer.
- `test_tree_conn_flag()` helper.
- APIs for connect, put, disconnect, lookup, and session logoff cleanup.

It includes `ksmbd_netlink.h` for tree connection flag/status values shared with userspace IPC.
