# sources/user-network-fs/samba/source3/smbd/smb2_process.c

## Purpose
Despite the SMB2 filename, this file is the smbd per-client process and packet-dispatch bootstrap for SMB1/SMB2. It receives initial packets, negotiates SMB1 versus SMB2, constructs SMB1 replies, maintains deferred open retry queues, creates connection/session/open tables, registers cluster and messaging handlers, sets up timers/signals/profiling, and runs the main tevent loop for a client connection.

## Important APIs, Types, And Functions
Key entry points include `receive_smb_talloc()`, `process_smb()`, `smbXsrv_connection_init_tables()`, `init_smb1_request()`, `smbd_add_connection()`, and `smbd_process()`. Deferred-open helpers include `push_deferred_open_message_smb()`, `schedule_deferred_open_message_smb()`, `remove_deferred_open_message_smb()`, `open_was_deferred()`, and `get_deferred_open_message_state()`, backed by `struct pending_message_list`. Connection setup uses `struct smbXsrv_client`, `struct smbd_server_connection`, and `struct smbXsrv_connection`. Messaging handlers cover forced disconnects, config reload, id-cache invalidation, CTDB IP release, and IP-dropped events.

## Control Flow
Connection setup starts in `smbd_process()`: create client and server-connection objects, initialize the pthread pool, install signals, call `smbd_add_connection()`, copy local/remote address metadata, reload services, optionally chroot, initialize file tables, oplocks, messaging handlers, keepalive/deadtime/housekeeping timers, directory pointers, profiling, and then enter `tevent_loop_wait()`. The first packet read handler only accepts NBSS session requests, SMB1 negprot bootstrap, or SMB2 negprot. Later `process_smb()` handles NBSS special messages, detects SMB2 headers when allowed, disables SMB2 for non-negprot SMB1 traffic, and dispatches to SMB1 or SMB2 processors. Deferred-open timers redispatch saved SMB1 buffers through `process_smb()` and remove processed queue entries.

## State And Persistence
State is per-process and mostly talloc-owned: connection lists, session/open tables, deferred open queue, event fds, timers, message registrations, id cache entries, profiling trace state, account policy handles, pthread pool, and address metadata. Persistent external state can be affected indirectly through CTDB IP registration, account policy DB initialization, log reopening/rotation, service reloads, and optional process chroot.

## Dependencies And Integration Points
This file sits between socket transport, NetBIOS session handling, SMB1/SMB2 protocol processors, CTDB clustering, Samba messaging, authentication/session tables, id cache, file and directory subsystems, oplocks, printing queues, loadparm configuration, pthreadpool tevent, and profiling. It also includes fallback SMB2-only receive/send code when SMB1 support is compiled out.

## Risks And Test Signals
High-value tests include SMB2-only initial negotiation, SMB1 negprot bootstrap into SMB2, rejection of invalid initial packet types, host allow/deny negative session response, deferred open scheduling/removal/retry ordering, CTDB release-IP clean termination, id-cache kill only when an id is in use, SIGHUP reload, deadtime idle shutdown, housekeeping reload/log checks, and chroot failure handling. Watch for connection state races during forced disconnect, use-after-free in deferred buffers, table initialization rollback leaving `protocol` stale, and event trace stackframe leaks.
