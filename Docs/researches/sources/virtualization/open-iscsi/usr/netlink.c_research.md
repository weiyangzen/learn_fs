# File Research: sources/virtualization/open-iscsi/usr/netlink.c

Purpose: Implements the open-iscsi userspace kernel IPC backend over `NETLINK_ISCSI`, exposing it as the global `struct iscsi_ipc *ipc`.

Key entry points:
- `ctldev_open()` allocates fixed transmit/receive buffers, opens a `NETLINK_ISCSI` socket, binds to the current pid and multicast group 1, and initializes the kernel destination address.
- `ctldev_close()` closes the control socket and frees buffers.
- `ctldev_handle()` reads and dispatches asynchronous kernel events.
- `ipc_register_ev_callback()` installs callbacks used to allocate, schedule, and free event contexts.
- `iscsi_nla_alloc()` allocates a netlink attribute with open-iscsi length macros.

Synchronous kernel commands:
- Session lifecycle: `kcreate_session()`, `kdestroy_session()`, `kunbind_session()`.
- Connection lifecycle: `kcreate_conn()`, `kdestroy_conn()`, `kbind_conn()`, `kstart_conn()`, `kstop_conn()`.
- Discovery and transport endpoints: `ksendtargets()`, `ktransport_ep_connect()`, `ktransport_ep_poll()`, `ktransport_ep_disconnect()`.
- Parameter paths: `kset_param()`, `kset_host_param()`, `kset_net_config()`.
- Stats and host data: `kget_stats()`, `kget_host_stats()`.
- CHAP table operations: `kget_chap()`, `kset_chap()`, `kdelete_chap()`.
- Flashnode operations: `kset_flashnode_params()`, `knew_flashnode()`, `kdel_flashnode()`, `klogin_flashnode()`, `klogout_flashnode()`, `klogout_flashnode_sid()`.
- Ping: `kexec_ping()` and `ksend_ping()`.

PDU streaming:
- `ksend_pdu_begin()` starts an in-memory `ISCSI_UEVENT_SEND_PDU` aggregate containing event header, iSCSI header, and data.
- `kwritev()` appends payload fragments to the aggregate for send-PDU operations, otherwise emits a netlink message immediately.
- `ksend_pdu_end()` sends the accumulated PDU and clears transmit state.
- `krecv_pdu_begin()` obtains an async receive context, points `recvbuf` at the PDU payload after the kernel event, and supports `-EAGAIN` for unrelated events.
- `kread()` copies from the current receive buffer.
- `krecv_pdu_end()` releases the event context and clears receive state.

Implementation notes:
- `__kipc_call()` serializes synchronous commands. It sends the request, peeks at incoming events, handles `ISCSI_KEVENT_IF_ERROR`, queues unrelated async events through `ctldev_handle()`, and only returns when the expected event type is available.
- Netlink send retries on `-ENOMEM` after sleeping, reflecting comments that kernel allocation can fail while the userspace path can wait.
- Fixed buffers are sized by `NLM_BUF_DEFAULT_MAX`, `PDU_SENDBUF_DEFAULT_MAX`, and `NLM_SETPARAM_DEFAULT_MAX`; oversized sends are treated as fatal bugs.
- `ctldev_handle()` recognizes create/destroy session, receive PDU, connection error, connection login state, unbind session, host link events, and ping completion. Unknown events are dropped after logging.
- Async connection events are matched by SID/CID to the in-memory session table and scheduled as `EV_CONN_RECV_PDU`, `EV_CONN_ERROR`, `EV_CONN_LOGIN`, or `EV_CONN_STOP`.
- `kexec_ping()` opens its own control device, sends a ping with a random pid, polls for up to 30 seconds, and matches completion by pid.

Dependencies and interactions:
- Depends on kernel ABI definitions from `iscsi_if.h`, transport/session state from `initiator.h` and `transport.h`, sysfs lookup via `iscsi_sysfs.h`, and timer helpers.
- Supplies the full `nl_ipc` vtable consumed by daemon/login/session code through the global `ipc`.
- Requires callback integration from the event loop/initiator layer to allocate and schedule receive contexts.

Filesystem/storage relevance:
- This is the userspace-to-kernel bridge that creates iSCSI kernel sessions/connections, pushes negotiated parameters, sends/receives iSCSI PDUs, receives connection failure events, and retrieves statistics for network block storage sessions.
