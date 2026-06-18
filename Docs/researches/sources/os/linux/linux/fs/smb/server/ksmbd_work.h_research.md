# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_work.h

This header defines per-request KSMBD work state.

Key contents:
- Work state enum: active, cancelled, closed.
- `struct aux_read` for auxiliary read buffers attached to a response.
- `struct ksmbd_work`, linking a request to connection/session/tree connect, request and response buffers, response iovecs, compound request offsets/FIDs, saved credentials, credits, transform buffer, state flags, RDMA invalidation data, async cancellation data, workqueue item, and request/async/file list nodes.
- Inline helpers to locate next/current response SMB2 buffer and next request SMB2 buffer, accounting for the RFC1002 header.
- Allocation/free, pool/workqueue, queue, iovec pinning, and interim response APIs.

This is the primary request context passed through SMB2 command handling.
