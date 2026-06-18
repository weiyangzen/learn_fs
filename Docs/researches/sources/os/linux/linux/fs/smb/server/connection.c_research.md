# File Research: sources/os/linux/linux/fs/smb/server/connection.c

This file manages KSMBD connection lifecycle, global connection tracking, receive loops, request accounting, writes, and transport startup/shutdown.

Main behavior:
- Maintains global `conn_list` hash under `conn_list_lock`.
- Optionally exposes procfs client information with address, dialect, credits, open files, running requests, and last active time.
- Uses a dedicated `ksmbd-conn-release` workqueue so final connection teardown can sleep safely even if the last put happens from non-sleepable context.
- `ksmbd_conn_alloc()` initializes NLS/Unicode state, sessions xarray, request lists, waitqueues, locks, credit state, async IDA, and refcounts.
- Request queue helpers account `req_running`, list synchronous requests, and release async work when dequeued.
- `ksmbd_conn_handler_loop()` is the per-connection receive loop: reads RFC1002 header, validates PDU size, allocates request buffer, reads the full PDU, validates SMB framing, and calls registered server callbacks.
- `ksmbd_conn_write()` serializes transport writes with `srv_mutex` and uses RFC1002 length from the first iovec.
- Transport init/destroy starts TCP and RDMA, creates proc entries, shuts down active sessions, and drains the global list.

The file abstracts transport operations but relies on TCP/RDMA implementations and server callbacks elsewhere.
