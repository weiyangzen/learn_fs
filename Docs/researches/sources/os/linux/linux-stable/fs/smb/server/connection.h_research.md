# File Research: sources/os/linux/linux-stable/fs/smb/server/connection.h

Read status: complete.

## Purpose
Defines ksmbd connection state, transport operation contracts, and connection lifecycle APIs.

## Main Contents
- Session/connection status enum values.
- `struct ksmbd_conn_stats`, `struct ksmbd_conn`, `struct ksmbd_conn_ops`, `struct ksmbd_transport_ops`, and `struct ksmbd_transport`.
- TCP timeout/backlog constants and global connection hash declarations.
- APIs for allocation, refcounting, request queueing, transport init/destroy, writes, RDMA I/O, handler loop, and status transitions.
- Inline status predicates/setters using `READ_ONCE()`/`WRITE_ONCE()`.

## Dependencies And Role
This is the central contract between transport code, work processing, SMB dialect logic, and session management.

## Risks
The connection struct contains many cross-module lifetimes. Status changes and xarray/session locking must remain consistent to avoid use-after-free, hung shutdown, or incorrect reconnect/session setup behavior.
