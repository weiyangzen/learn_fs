# File Research: sources/os/linux/linux/fs/smb/server/connection.h

This header defines the central `struct ksmbd_conn` and transport interfaces.

Key contents:
- Connection status enum for new, good, exiting, reconnect, negotiate/setup, and releasing states.
- `struct ksmbd_conn_stats` with open file and served request counters.
- `struct ksmbd_conn`, containing dialect ops/values, locks, network address, transport, NLS/Unicode state, session xarray, request lists, credits, NTLMSSP state, preauth state, auth mechanism selection, signing/encryption negotiation, async IDA, and release work.
- `struct ksmbd_conn_ops` server callbacks for processing and termination.
- `struct ksmbd_transport_ops` for disconnect/shutdown/read/writev/RDMA read/write/free.
- Public connection lifecycle, lookup, write, RDMA, queue, callback, lock, refcount, and transport APIs.
- Inline status testers/setters using `READ_ONCE()`/`WRITE_ONCE()`.

This is the main contract between KSMBD protocol handling and the underlying transport/session machinery.
