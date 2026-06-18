# File Research: sources/virtualization/open-iscsi/usr/mgmt_ipc.h

Purpose: Declares the daemon/admin IPC command protocol, request/response wire structures, and management IPC server functions.

Key definitions:
- `ISCSIADM_NAMESPACE` names the abstract Unix socket namespace environment key.
- `iscsiadm_cmd_e` enumerates management commands, including session login/logout/sync/stats/info, connection add/remove, config reads, send-targets discovery, immediate stop, and discovery notifications.
- `iscsiadm_req_t` carries a command, optional payload length, and command-specific union fields for session record/SID, connection SID/CID, send-targets host/address, and host parameter setting.
- `iscsiadm_rsp_t` carries the command, an `ISCSI_ERR` result, and result unions for stats, config string, or session/connection state.
- `MGMT_IPC_GETSTATS_BUF_MAX` sizes the stats response buffer for base and custom iSCSI stats.
- `mgmt_ipc_fn_t` is the handler signature for a queue task.

Declared APIs:
- `mgmt_ipc_write_rsp()`
- `mgmt_ipc_listen()`
- `mgmt_ipc_systemd()`
- `mgmt_ipc_close()`
- `mgmt_ipc_handle()`
- `mgmt_ipc_handle_legacy()`

Dependencies and interactions:
- Includes `types.h`, `iscsi_if.h`, and `config.h` for protocol, kernel-interface, and size definitions.
- Embeds `node_rec_t` in session requests, making this IPC ABI carry full login records.

Filesystem/storage relevance:
- The header is the local control ABI between admin tooling and the iSCSI daemon for operations that create, tear down, inspect, or discover storage sessions.
