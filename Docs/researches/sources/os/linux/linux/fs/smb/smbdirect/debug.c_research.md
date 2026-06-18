# File Research: sources/os/linux/linux/fs/smb/smbdirect/debug.c

Provides a legacy proc/debug reporting helper for SMB Direct connection state.

Key entry point:
- `smbdirect_connection_legacy_debug_proc_show()` emits human-readable state into a `seq_file`.

Reported data:
- SMB Direct protocol version and transport status.
- Negotiated receive credit max, send credit target, max send/receive sizes, fragmented send/receive sizes.
- Keepalive interval, max RDMA read/write size, and caller-supplied RDMA read/write threshold.
- Receive buffer get/put counters, empty-send counter, reassembly enqueue/dequeue counters, reassembly data length and queue length.
- Current send and receive credits, receive credit target, pending send count.
- MR responder resources, FRMR depth, MR type, ready MR count, and used MR count.

Dependencies:
- Reads `struct smbdirect_socket` fields defined in `socket.h`.
- Uses `seq_file` output and is exported with `EXPORT_SYMBOL_GPL`.

Maintenance notes:
- This is observational only and does not lock around counters/queue lengths; values are snapshots suitable for diagnostics, not strict consistency checks.
