# File Research: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.h

Purpose: Defines the local broadcast protocol used between open-iscsi userspace and the uIP helper process.

Key definitions:
- `ISCSID_UIP_NAMESPACE` names the abstract namespace used for uIP IPC.
- `iscsid_uip_cmd_e` enumerates uIP commands: unknown, get iface, and ping.
- `iscsid_uip_broadcast_header_t` carries command and payload length.
- `iscsid_uip_broadcast_t` carries either an interface record or a ping record with interface, destination address, data length, and status pointer.
- `iscsid_uip_mgmt_ipc_err_e` enumerates uIP IPC result states including OK, generic error, not found, no memory, device up, and device initializing.
- `iscsid_uip_rsp_t` carries command, uIP IPC error, and iSCSI ping status code.

Declared APIs:
- `uip_broadcast_params()`
- `uip_broadcast_ping_req()`

Dependencies and interactions:
- Includes generic types, kernel iSCSI interface definitions, config, management IPC declarations, initiator state, and transport types.

Filesystem/storage relevance:
- Defines the protocol shape for offload-network setup and ping checks that gate access to iSCSI storage sessions on supported hardware transports.
