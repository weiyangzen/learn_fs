# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_bad_event.c

Purpose: implements the IDS model that reacts to login and system lifecycle audit events. It creates and tears down sessions, scores origins for failed or forbidden logins, and triggers origin-level reactions.

Important APIs and data: exports `process_bad_event_model`. Local helpers `start_session`, `end_session`, and `terminate_sessions` coordinate origin/session state with auparse-normalized fields.

Control flow: for boot/shutdown, all sessions are destroyed. For `AUDIT_USER_LOGIN`, `start_session` extracts `addr`, subject kind/account, result, and session id; creates/fetches an origin; scores service/root/failed login conditions; and creates a session for successful user logins. For logout, `end_session` removes non-daemon sessions. After event-specific handling, current origin karma is checked against `option_origin_failed_logins_threshold` and `do_reaction` is called if unblocked.

State and persistence: mutates in-memory origin AVL state and session AVL state. System boot/shutdown clear session state, but origin state persists until process restart or explicit destroy.

Dependencies and integration: depends on auparse normalization, libaudit event constants, `origin.c`, `session.c`, global `debug`, and `reactions.c`. It intentionally ignores IDS-generated anomaly events to avoid feeding on its own responses.

Risks: IPv4-only address conversion stores invalid or absent addresses as `-1`, which can aggregate unrelated unknown origins. `inet_pton` return is not checked. Account ownership transfer to `new_session` is subtle and depends on setting `acct = NULL` after successful creation.

Test signals: audit events for successful login, failed login, root/service account login, logout, daemon session, and system boot/shutdown should drive expected session/origin counts and reaction calls.
