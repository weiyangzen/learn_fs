# File Research: sources/virtualization/open-iscsi/usr/iscsid_req.c

## Purpose
`iscsid_req.c` implements client-side helpers for sending management requests to `iscsid` over abstract UNIX sockets, plus a helper for broadcasting requests to the uIP daemon.

## Main APIs
- `iscsid_startup()` reads `iscsid.startup` from `CONFIG_FILE` and runs that command when auto-start is requested and the daemon is not reachable.
- `ipc_connect()` opens an AF_LOCAL stream socket to an abstract namespace, attempts `connect()` with exponential backoff up to `MAXSLEEP`, optionally starts `iscsid` on first `ECONNREFUSED`, and returns open fd or an open-iscsi error.
- `iscsid_set_namespace()` switches the management socket namespace between the normal `ISCSIADM_NAMESPACE` and a PID-suffixed namespace used by `iscsistart`.
- `iscsid_request()` connects and writes an `iscsiadm_req_t`.
- `iscsid_response()` polls, receives an `iscsiadm_rsp_t` with `MSG_WAITALL`, closes the fd, returns daemon error status, and verifies response command matches request command.
- `iscsid_exec_req()` combines request and response.
- `iscsid_req_by_rec*()` and `iscsid_req_by_sid*()` build common session requests by node record or sid, with synchronous and asynchronous variants.
- `uip_broadcast()` connects to the uIP namespace, writes a buffer, optionally sets nonblocking flags, retries reads, interprets get-iface and ping responses, and maps daemon status to open-iscsi errors.

## Integration Notes
This module is used by `iscsiadm`, `iscsistart`, and daemon recovery paths to issue management IPC commands. It depends on `mgmt_ipc.h`, `uip_mgmt_ipc.h`, config parsing, and abstract socket addressing from `iscsi_util.c`.

## Risk Notes
- `iscsid_response()` closes the fd unconditionally after response handling; callers must not reuse it.
- Timeout handling is per poll; callers pass `-1` for indefinite waits on long operations such as boot login.
- Auto-start depends on a config-file shell command, so deployment configuration controls whether CLI operations can start the daemon.
