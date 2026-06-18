# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_server.c

## Purpose

`smb_server.c` is the SMB server management core. It owns global initialization, per-zone server lifecycle, service configuration, startup/shutdown, listener sockets, session creation/destruction, kstats, counters, event wait/notify objects, spool queues, share disconnect, server lookup/refcounting, and ioctl-facing management operations.

## Main Interfaces

- Global lifecycle: `smb_server_g_init()`, `smb_server_g_fini()`, `smb_server_get_count()`.
- Per-server lifecycle: `smb_server_create()`, `smb_server_delete()`, `smb_server_configure()`, `smb_server_start()`, `smb_server_stop()`, `smb_server_is_stopping()`.
- Management ioctls: `smb_server_spooldoc()`, `smb_server_set_gmtoff()`, `smb_server_numopen()`, `smb_server_enum()`, `smb_server_session_close()`, `smb_server_file_close()`.
- Share/session operations: `smb_server_share_lookup()`, `smb_server_unshare()`, `smb_server_lookup_user()`, `smb_server_logoff_ssnid()`.
- Lookup/reference: `smb_server_lookup()`, `smb_server_release()`.
- Counters: `smb_server_inc_*`, `smb_server_dec_*`, `smb_server_add_rxb()`, `smb_server_add_txb()`, `smb_server_inc_req()`.
- Event API: `smb_event_create()`, `smb_event_destroy()`, `smb_event_txid()`, `smb_event_wait()`, `smb_event_notify()`, `smb_server_cancel_event()`.
- Spool API: `smb_spool_add_fid()`, `smb_spool_add_doc()`.

## Behavior And Data Flow

Global init initializes VOP/FEM layers, share/codepage/mbc/node/lease subsystems, kmem caches for core SMB object types, and global server/session-zombie lists. Global fini asserts no servers remain and tears those subsystems down in reverse.

`smB_server_create()` enforces one server per zone, allocates and initializes `smb_server_t`, persistent handle and lease hash tables, session/event/spool lists, dispatch stats arrays, timers, request queue, kdoor/kshare/kstat state, threshold counters, and inserts the server into the global list.

`smB_server_start()` transitions configured servers to running. It may create a kernel process to own SMB worker LWPs, initializes root SMB node state, creates a special server session and root user, starts kshare, creates notify/worker/receiver taskqs, opens userland doors, starts the timer thread, creates TCP and optional NetBIOS listeners, and starts SMB export. On failure it calls `smb_server_shutdown()`.

Shutdown stops listeners first, disconnects all sessions, cancels events and threshold waits, waits for the session list to drain, closes doors, stops exports and shares, stops timers, logs off root/server-session state, destroys taskqs, shuts down durable handles, releases root node state, and stops the optional server process.

Listener code creates AF_INET/AF_INET6 sockets, sets socket options, binds/listens on port 445 and optionally 139, accepts connections, sets TCP options, creates sessions, inserts them under max-connection enforcement, and dispatches receiver tasks. Receiver completion destroys or quarantines sessions depending on whether they reached clean shutdown.

## Kstats And Configuration

`smB_server_kstat_init()` creates raw and legacy kstats. Updates report active sessions, users, trees, files, pipes, bytes sent/received, request counts, server utilization, and SMB1/SMB2 dispatch stats. Configuration storage copies all relevant daemon-provided knobs including worker limits, keepalive, signing, oplocks, sync, NetBIOS/IPv6/printing, mount traversal, protocol min/max, encryption, ciphers, signing algorithms, credits, machine UUID, negotiation token, native strings, domain, FQDN, hostname, and comments. Required encryption forces max protocol to at least SMB 3.0.

## Event And Spool Handling

Event objects are server-list members with txids, timeouts, mutex/cv state, notification and cancellation flags. `smb_event_wait()` loops in one-second increments until notified, canceled, or timed out. Shutdown cancels all events.

Print spool handling maintains one list of spool documents and another list of closed FIDs. Close queues a FID and wakes `smb_server_spooldoc()`, which pops a FID, finds/removes the matching spool document, and returns path/user/IP/spool number to userland.

## Dependencies

This file coordinates nearly every SMB subsystem: nodes, shares, sessions, users, trees, ofiles, oplocks/durable handles, leases, kdoors, filesystem ops, taskq, kernel sockets, kstats, DTrace, thresholds, request queues, exports, and printing.

## Notable Invariants And Risks

- Server state transitions are guarded by `sv_mutex`; deletion waits for `sv_refcnt` to drain.
- New server lookup refuses `SMB_SERVER_STATE_DELETING`.
- Shutdown must stop listeners before disconnecting sessions to prevent new work during teardown.
- It waits for session readers/workers to finish before destroying taskqs and shared server-session resources.
- Session objects that fail clean shutdown are moved to a zombie list for debugging instead of being freed.
- `smb_server_logoff_ssnid()` is careful to wait for durable handles to become orphaned before reconnect can reuse them.
- Socket listener failures during startup can leave partial listener state; shutdown handles cleanup.
- The file is concurrency-critical: global lists, server lists, session lists, event lists, spool lists, and refcounts all have distinct locking expectations.
