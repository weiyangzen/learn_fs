# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_conn_sm.h

This header defines the IDM connection state machine event/state vocabulary and related helpers.

Key definitions:
- Timeouts: `IDM_LOGIN_SECONDS`, `IDM_LOGOUT_SECONDS`, `IDM_CLEANUP_SECONDS`.
- `IDM_CONN_EVENT_LIST()` enumerates initiator, target, and common connection events.
- `idm_conn_event_t` includes connect/login/logout/async-drop/transport-fail/misc/protocol-error/reinstate/enable-datamover events.
- `CONN_STATE_LIST()` defines connection states from free, transport wait/up, login, logged-in, logout, cleanup, init error, enable datamover, rejected/wait-send-done, complete.
- Optional string tables are emitted under `IDM_CONN_SM_STRINGS`.

Timer safety macros:
- `IDM_SM_TIMER_CHECK(ic)` warns/asserts if an existing timeout is still set before scheduling another.
- `IDM_SM_TIMER_CLEAR(ic)` cancels and clears a state-machine timeout.
- The comment documents a historical panic risk from stale login timeout callbacks after connection close.

PDU event handling:
- `idm_pdu_event_type_t`: none, RX PDU, TX PDU.
- `idm_pdu_event_action_t`: send protocol error, forward, or drop.
- `idm_conn_event_ctx_t` carries event context, PDU event type, and forwarded state.

Functions:
- State machine init/fini, client notification, event dispatch, locked event dispatch, connection reinstatement, TX/RX PDU event helpers, and state string lookup.

Notes:
- The header contains a duplicated declaration of `idm_conn_event`; this is harmless in C headers but notable.
- It is tightly coupled to `idm_conn_t` fields such as `ic_state_timeout`, `ic_state`, and `ic_last_state`.

Relevance:
- Governs iSCSI login/logout/full-feature connection lifecycle, critical for stable block storage sessions.
