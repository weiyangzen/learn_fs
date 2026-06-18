# File Research: sources/os/linux/linux/fs/smb/server/transport_ipc.c

Implements Generic Netlink IPC between the kernel ksmbd server and the user-space ksmbd tools daemon.

Key behaviors:
- Registers a Generic Netlink family with event operations for startup, login/share/tree/RPC/SPNEGO responses, and unsupported event rejection.
- Maintains a hash table of outstanding IPC requests keyed by handle, with wait queues for synchronous request/response correlation.
- Validates daemon/kernel protocol version on inbound messages.
- Handles daemon startup, populating `server_conf` with signing, flags, port, IPC timeout, deadtime, fake fs caps, protocol bounds, max credits, max connections, interfaces, NetBIOS/server/workgroup strings, SMBDirect I/O size, and domain SID.
- Sends heartbeat requests and schedules a delayed heartbeat watchdog; missing daemon response transitions server state to resetting and queues reset work.
- Allocates and frees IPC message handles through ksmbd IDA helpers.
- Validates variable-length responses for RPC payload size, SPNEGO session key/blob lengths, share config payload/veto-list sizing, and extended-login group count.
- Provides request APIs for login, extended login, share config, tree connect/disconnect, logout, SPNEGO auth, and RPC open/close/read/write/ioctl.
- Enforces payload caps via `KSMBD_IPC_MAX_PAYLOAD` for SPNEGO and RPC data-bearing requests.

Dependencies:
- Ties together user/session/share/tree management, TCP/RDMA startup configuration, connection state, and server control work.
- Uses Generic Netlink, IDA, hash tables, wait queues, mutex/rwsem locking, and delayed work.

Role in subsystem:
- The trust boundary and configuration/authentication bridge between in-kernel SMB serving and the privileged user-space daemon.
