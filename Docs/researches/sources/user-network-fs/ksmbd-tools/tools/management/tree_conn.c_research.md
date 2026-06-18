# sources/user-network-fs/ksmbd-tools/tools/management/tree_conn.c

## Purpose

`tree_conn.c` authorizes and creates SMB tree connections between authenticated accounts and configured shares. It checks session capacity, bad-password policy, share existence, connection limits, host allow/deny maps, guest restrictions, and user access maps before binding a tree connection into session state. The source was read as a complete 227-line file.

## Important APIs, Types, and Functions

Public functions are `tcm_handle_tree_connect`, `tcm_handle_tree_disconnect`, and `tcm_tree_conn_free`. Internal helper `new_ksmbd_tree_conn` allocates a connection object. The file manipulates `ksmbd_tree_connect_request`, `ksmbd_tree_connect_response`, `ksmbd_tree_conn`, share flags, user flags, and global config fields.

## Control Flow

Connect allocates a connection, checks session capacity, resolves the share, mirrors share access flags into connection flags, opens the share connection, evaluates host maps, enforces anonymous/guest restrictions, resolves guest or named users, applies admin/invalid/read/write/valid user maps in precedence order, then binds the connection via `sm_handle_tree_connect`. Error paths free the connection and release share/user references. Disconnect delegates to session management.

## State and Persistence Behavior

The file creates in-memory tree connection objects. Long-lived state is retained in session lists and share connection counters until disconnect/free. It clears a share's update flag after a successful bind.

## Dependencies and Integration Points

It depends on session, share, user, tools, and kernel IPC structs. It is invoked by the mountd worker's tree-connect and tree-disconnect IPC handlers.

## Risks and Edge Cases

Error cleanup calls both `tcm_tree_conn_free(conn)` and separate `shm_close_connection(share)` / `put_ksmbd_share(share)`; because `conn->share` is only assigned on success this is intentional but fragile. Access-map return conventions distinguish absent maps from explicit misses. Guest fallback depends on configured guest users existing in the user manager.

## Test Signals

Exercise each response status: no share, no user, invalid user, host denied, too many sessions, too many share connections, guest denied, admin/read/write-list overrides, reload update flag clearing, and disconnect idempotency.
