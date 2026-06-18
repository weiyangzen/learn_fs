# File Research: sources/virtualization/open-iscsi/usr/mgmt_ipc.c

Purpose: Implements the local management IPC server used by `iscsiadm` and related clients to send requests to `iscsid`.

Key entry points:
- `mgmt_ipc_listen()` obtains a systemd-passed socket when available or creates/listens on an abstract Unix-domain socket.
- `mgmt_ipc_systemd()` validates `LISTEN_PID` and `LISTEN_FDS` and returns fd 3 when exactly one socket is passed.
- `mgmt_ipc_close()` exits the event loop and closes the listening fd.
- `mgmt_ipc_handle()` and `mgmt_ipc_handle_legacy()` accept a client, authorize it, read a request, dispatch a handler, and send a response.
- `mgmt_ipc_write_rsp()` serializes `iscsiadm_rsp_t`, closes the per-request fd, frees any payload, and conditionally frees the task object.

Command handling:
- Session operations dispatch to `session_login_task()`, `session_logout_task()`, and `iscsi_sync_session()`.
- `MGMT_IPC_SESSION_STATS` finds a session by SID and calls `ipc->get_stats()`.
- `MGMT_IPC_SEND_TARGETS` calls `iscsi_host_send_targets()`.
- `MGMT_IPC_SESSION_INFO` returns daemon-side session and connection state.
- Config commands return initiator name, initiator alias, or config filename from `dconfig`.
- Immediate stop exits the event loop.
- Connection add/remove currently return generic error.
- Notify add/delete node/portal commands parse string-vector payloads but route to placeholder handlers that return success.

Implementation notes:
- Authorization defaults to Linux `SO_PEERCRED` UID check requiring UID 0. Legacy mode also resolves the peer username and requires `"root"`.
- Request payloads are bounded to `EXTMSG_MAX` (64 KiB) and allocated with one extra byte for possible NUL termination.
- Extended notification payloads encode repeated strings as a 32-bit length followed by raw bytes; `mgmt_ipc_parse_strings()` rewrites separators in place and returns an argv-style array.
- The dispatch table `mgmt_ipc_functions[]` maps command enum values to handler functions and rejects unknown or out-of-range commands.
- `queue_task_t->allocated` distinguishes standalone IPC tasks from tasks embedded in larger recovery structures.

Dependencies and interactions:
- Depends on daemon/session modules (`iscsid.h`, `initiator.h` through task handlers), IDBM/config, event loop control, transport, sysdeps, kernel IPC vtable, and error-code helpers.
- Writes responses with `ISCSI_ERR_*`/`ISCSI_SUCCESS` semantics expected by `iscsid_req` clients.

Filesystem/storage relevance:
- This file is the daemon command ingress for login/logout, target discovery, statistics, and session status. It connects administrative storage operations to the running userspace iSCSI session manager.
