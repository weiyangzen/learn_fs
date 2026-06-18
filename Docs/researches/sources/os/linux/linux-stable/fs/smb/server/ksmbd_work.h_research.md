# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_work.h

Read status: complete.

## Purpose
Defines the per-request ksmbd work object and workqueue/iovec helper APIs.

## Main Contents
- Work state enum values.
- `struct aux_read`.
- `struct ksmbd_work` containing connection/session/tree pointers, request/response buffers, compound offsets/FIDs, credentials, credits, transform state, async cancel data, response iovecs, and list nodes.
- Inline helpers for current/next compound request and response buffers.
- Allocation, free, pool, workqueue, response pinning, and interim response APIs.

## Dependencies And Role
This is the request execution context shared by SMB command handlers, transport code, auth, and management paths.

## Risks
Many subsystems store transient state in `ksmbd_work`; buffer offset helpers assume SMB response/request buffers include the 4-byte RFC1002 prefix.
