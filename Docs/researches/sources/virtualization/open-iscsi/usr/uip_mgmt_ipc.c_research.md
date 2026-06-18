# File Research: sources/virtualization/open-iscsi/usr/uip_mgmt_ipc.c

Purpose: Sends management broadcasts from `iscsid`/admin code to the uIP helper for offload transports that need userspace IP configuration or ping handling.

Key entry points:
- `uip_broadcast_params()` sends an `ISCSID_UIP_IPC_GET_IFACE` broadcast containing an `iface_rec`.
- `uip_broadcast_ping_req()` sends an `ISCSID_UIP_IPC_PING` broadcast containing interface data, destination address, and ping payload length, and waits for status.

Implementation notes:
- Both functions populate `struct iscsid_uip_broadcast`, set command and payload length, copy the relevant interface record, and call `uip_broadcast()`.
- `uip_broadcast_params()` uses `O_NONBLOCK` and does not request a status pointer.
- `uip_broadcast_ping_req()` accepts IPv4 and IPv6 destination addresses, rejects unknown address families with `ISCSI_ERR_INVAL`, stores `datalen`, and passes `status` through to `uip_broadcast()`.

Dependencies and interactions:
- Uses `uip_mgmt_ipc.h` protocol structures, `iscsid_req.h` for `uip_broadcast()`, logging, and iSCSI error constants.
- Referenced by transport templates such as `bnx2i` and `qedi` for `.set_net_config` and `.exec_ping`.

Filesystem/storage relevance:
- Supports hardware/offload iSCSI transports whose network setup is delegated to a uIP companion process before or during storage session establishment.
