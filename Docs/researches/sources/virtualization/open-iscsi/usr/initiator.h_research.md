# File Research: sources/virtualization/open-iscsi/usr/initiator.h

This header defines the core runtime data structures and public APIs for the open-iscsi daemon initiator.

Key contents:
- Default config paths:
  - `CONFIG_FILE`
  - `INITIATOR_NAME_FILE`
  - `PID_FILE`
  - DB lock files under `LOCK_DIR`
- Connection-aware logging macros: `conn_info`, `conn_warn`, `conn_error`, `conn_debug`.
- Recovery-stage enum `iscsi_session_r_stage_e`.
- Login result enums:
  - `conn_login_status_e`
  - `enum iscsi_login_status`
- Actor/event enum `iscsi_event_e`.
- `iscsi_login_context_t`, holding login PDU state, buffers, auth client, response status, timeout, and queue task.
- `iscsi_conn_t`, the daemon-side connection record:
  - ids and session pointer
  - login and receive contexts
  - logout queue task
  - receive/data buffer
  - connection state
  - timers
  - event context pool
  - login stage/status
  - socket or transport endpoint handle
  - TCP settings
  - login/logout/auth/noop timeouts
  - statsn and negotiated digest/data segment values
- `struct iscsi_ev_context`, actor plus connection/event payload.
- `queue_task_t`, management IPC request/response plus optional payload.
- `iscsi_session_t`, the daemon-side session record:
  - transport, session id, host number, iface/netdev
  - original node record
  - negotiated iSCSI parameters
  - target/initiator identifiers
  - CHAP/auth buffers
  - connection array
  - recovery/reopen state
  - error-handling timeouts
  - notification task pointer
- Login/session constants, digest constants, and irrelevant-key bit flags.
- Prototypes for login code, kernel transport endpoint helpers, TCP I/O helpers, session tasks, discovery, common setup, and session lookup.

Important dependencies:
- Includes protocol, kernel ABI, auth, management IPC, actor, list, config, and logging headers.
- Provides the common struct definitions consumed by `initiator.c`, `initiator_common.c`, and `io.c`.

Filesystem/storage relevance:
- These structures are the in-memory model of iSCSI sessions and connections. They bridge user-space configuration to kernel transport/session state and ultimately to visible SCSI/block devices.

Notable details:
- Connection data buffer is sized with `ISCSI_DEF_MAX_RECV_SEG_LEN`.
- Only `ISCSI_CONN_MAX` connections are embedded per session.
- `CONTEXT_POOL_MAX` is fixed at 32 per connection.
- The header documents that some transports have kernel-managed endpoints, while TCP uses a socket fd cast/stored through the transport endpoint handle path.
