# File Research: sources/virtualization/open-iscsi/usr/io.c

This file implements low-level iSCSI connection I/O for TCP sockets and IPC-backed kernel I/O. It handles socket creation, binding, TCP options, connect/poll/disconnect, PDU send, and PDU receive.

Major responsibilities:
- Uses `SIGALRM` and a file-static `timedout` flag to bound blocking socket operations.
- Validates that an iface-bound netdev has an address of the expected family before binding.
- Binds software TCP sessions to a netdev using `SO_BINDTODEVICE` when the iface is bound by hardware address or netdev.
- Creates TCP sockets, sets `TCP_NODELAY`, optional receive/send window sizes, and optional TCP congestion control.
- Supports nonblocking connect and subsequent poll-based completion.
- Disconnects TCP sockets and uses abortive close with `SO_LINGER` when not in clean logout.
- Sends iSCSI PDUs by writing header/AHS and data plus 4-byte alignment padding through `writev()` or `ipc->writev()`.
- Receives iSCSI PDUs by reading fixed header, rejecting unsupported additional header segments, validating data length against caller buffer, reading data and padding, and logging login/text content.
- Wraps IPC PDU transactions with `send_pdu_begin/end` and `recv_pdu_begin/end`.

Important dependencies:
- Uses iface binding helpers from `iface.c`.
- Uses net helper `net_get_netdev_from_hwaddress()`.
- Uses global `ipc` and transport/session runtime state from `initiator.h`.
- Uses iSCSI protocol macros for opcodes, padding, and 24-bit data length conversion.

Filesystem/storage relevance:
- This is the userspace data/control PDU path for software iSCSI login, discovery, logout, NOP, text, and async handling. It does not carry SCSI read/write data once the kernel session is active, but it is essential for establishing and maintaining block-storage sessions.

Notable constraints and risks:
- Header and data digest arguments are currently unused in these routines.
- Additional header segments are not supported on receive.
- The static `timedout` flag and process-wide `SIGALRM` approach are simple but fragile in a multi-operation/evented daemon.
- `iscsi_io_tcp_connect()` returns `-1` on bind failure without closing the just-created socket in that branch.
- PDU receive returns `-EIO` for timeout/failure and otherwise returns bytes read excluding padding.
