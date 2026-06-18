# File Research: sources/os/linux/linux-stable/fs/smb/server/connection.c

Read status: complete.

## Purpose
Manages ksmbd connection objects, per-connection handler loops, request admission, transport writes, RDMA hooks, connection shutdown, and proc client reporting.

## Main Responsibilities
- Allocate/free `ksmbd_conn`, including NLS/Unicode state, xarrays, IDAs, request lists, locks, and refcounts.
- Maintain the global connection hash and optional `/proc` clients view.
- Defer final transport/socket cleanup to a workqueue so last-put cleanup can sleep safely.
- Enqueue/dequeue running requests and async work, updating idle wait queues.
- Read RFC1002-framed SMB PDUs, validate sizes, allocate request buffers, and dispatch through registered process callbacks.
- Serialize transport writes and expose RDMA read/write transport operations.
- Stop all sessions/transports during server teardown.

## Dependencies And Role
Sits between TCP/RDMA transports and SMB request processing. It coordinates with sessions, work items, server config, stats, and transport ops.

## Risks
Critical risks are connection refcount lifetime, request counters during disconnect, RFC1002 PDU size validation, teardown ordering, and avoiding sleepable socket cleanup from non-sleeping contexts.
