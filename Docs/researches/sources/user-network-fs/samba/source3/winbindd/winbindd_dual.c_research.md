# sources/user-network-fs/samba/source3/winbindd/winbindd_dual.c

## Purpose
Provides winbind's parent/child process infrastructure. The parent forks per-domain, idmap, and locator children to isolate blocking network/domain work, multiplexes async requests through queues, relays process-control messages, and manages child reinitialization, online/offline state, trust password rotation, signal handling, and cache flushing.

## Important APIs, Types, And Control Flow
`wb_child_request_send/recv()` serializes one request to one child over a socketpair using `wb_simple_trans_send()`, preserving the request when callers abandon an in-flight transaction. `wb_domain_request_send/recv()` queues requests per domain, picks the child with the shortest queue, initializes uninitialized domains via `wbint_InitConnection`, optionally obtains a DC with `wb_dsgetdcname_send()`, then delegates to `wb_child_request_send()`. `setup_child()` initializes a `winbindd_child` queue, log path, socket sentinel, domain pointer, and internal wbint binding handle. `fork_domain_child()` creates the socketpair, forks, reinitializes messaging/logging/db state in the child, registers child message handlers, starts domain online/setup timers, and enters the tevent loop with `child_handler()`. Message handlers relay debug, reload, disconnect, online/offline, IP-dropped, dump-domain, and status requests across parent and children.

## State And Persistence
Maintains child PIDs, sockets, monitor fds, per-child queues, per-domain queues, log file names, domain initialized/online/startup fields, lockout-policy timers, machine-password-change timers, and inherited messaging registrations. It unlinks the winbindd socket and PID file only on parent termination. Machine-password changes update secrets through lower-level trust code.

## Dependencies And Integration Points
Integrates with tevent queues/signals/fds, Samba messaging, domain list management, idmap and locator children, generated wbint binding handles, winbind cache, connection manager, passdb/secrets, netlogon credential code, and OS socket/fork primitives.

## Risks And Test Signals
High-risk areas are orphaned requests, child death while queued, socket closure detection, domain queue starvation, stale domain pointers after reload, fork reinitialization leakage, timer races in clustered password changes, and online/offline propagation. Test with slow DC calls, child kill/restart, SIGHUP/reload, SIGTERM cleanup, multiple domain children, abandoned client requests, offline logon transitions, machine password expiry, and debug traceid propagation.
