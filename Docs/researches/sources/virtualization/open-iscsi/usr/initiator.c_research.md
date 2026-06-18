# File Research: sources/virtualization/open-iscsi/usr/initiator.c

This is the main iSCSI initiator slow-path/session management implementation. It drives session creation, connection establishment, login negotiation, recovery/reopen, logout, async event handling, userspace NOP handling, session resync, and IPC event callback registration.

Major responsibilities:
- Allocates and manages per-connection event contexts from a fixed pool.
- Creates and destroys `iscsi_session_t` and leading connection state.
- Maps login response statuses and iSCSI status class/detail into retry, redirect, fatal, auth-failure, or success outcomes.
- Initializes connection timeouts, NOP settings, TCP options, negotiated parameters, and portal address resolution.
- Performs initial connection and login scheduling through the actor/event system.
- Handles login timeouts, transport errors, kernel-reported connection errors, redirects, and recovery stages.
- Starts full-feature phase after login by setting negotiated params, starting the kernel connection, scanning the host, and scheduling userspace NOPs when needed.
- Sends logout PDUs, handles logout timeout, unbinds sessions when supported, and shuts down/destroys kernel/user session state.
- Handles incoming NOP-In, logout responses, async events, and login responses.
- Supports login-offload transports by waiting for kernel connection-state notifications instead of doing all login negotiation in userspace.
- Supports session sync after daemon restart or external session creation by reconstructing userspace state from node record and sysfs session id.
- Registers `iscsi_ipc_ev_clbk` callbacks for async firmware/session creation/destruction and per-connection event scheduling.

Key state machines:
- Connection states are interpreted across `ISCSI_CONN_STATE_XPT_WAIT`, `IN_LOGIN`, `LOGGED_IN`, `IN_LOGOUT`, `LOGOUT_REQUESTED`, and `CLEANUP_WAIT`.
- Recovery stages use `R_STAGE_NO_CHANGE`, `SESSION_CLEANUP`, `SESSION_REOPEN`, `SESSION_REDIRECT`, and `SESSION_DESTOYED`.
- Login error handling distinguishes initial login retry timeout, fatal login errors, auth failures, redirected retries, recovery reconnects, and cleanup.
- Reopen paths honor `DefaultTime2Wait`, reopen counters/max, reconnect delay constants, and whether the reopen follows redirect or ordinary failure.

Important entry points:
- `session_login_task()` starts login for a node record and internally retries when host/offload readiness is not available yet.
- `session_logout_task()` logs out a running session, with safe-logout checks against mounted/in-use storage.
- `iscsi_sync_session()` reconstructs daemon state for an existing kernel session and starts recovery.
- `iscsi_host_send_targets()` asks offload-capable transports to perform SendTargets discovery.
- `free_initiator()` releases all sessions and transports.
- `iscsi_initiator_init()` registers IPC callbacks.

Important dependencies:
- Depends on `transport`, `ipc`, sysfs helpers, IDBM, management IPC, actor/event scheduling, SCSI sense parsing, kernel error translation, and config defaults.
- Calls shared setup functions from `initiator_common.c`.
- Calls socket/PDU helpers from `io.c`.

Filesystem/storage relevance:
- This is the daemon control path that turns persisted target records into active kernel iSCSI sessions, which then expose remote SCSI LUNs as local block devices. It also performs host scans and queue-depth setup after login.

Notable implementation constraints and risks:
- Only the leading connection is fully handled in several places; comments mark multi-connection login/logout as TODO.
- Recovery depends on actor scheduling and context-pool availability; leaks are logged if allocated contexts remain during teardown.
- Some shutdown paths call response-writing helpers through task pointers that may be NULL depending on error source; safety depends on downstream helper behavior.
- Fatal/auth login failures force the reopen counter to its max to stop retry loops.
- `R_STAGE_SESSION_DESTOYED` is misspelled in the enum and usage, but consistently named.
