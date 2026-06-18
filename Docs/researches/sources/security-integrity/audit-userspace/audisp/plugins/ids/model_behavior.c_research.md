# sources/security-integrity/audit-userspace/audisp/plugins/ids/model_behavior.c

Purpose: scores user sessions based on suspicious audited behavior, especially IDS-tagged audit rules and anomaly records, then triggers session or origin reactions.

Important APIs and data: exports `process_behavior_model`. Local helpers `process_plain_syscalls` and `process_anomalies` inspect auparse event type, key, and session id.

Control flow: syscall events are filtered to audit keys beginning with `ids-`; known keys add fixed session score weights: recon 2, archive 5, mkexec 4, and connections 6. Fanotify/AVC/anomaly events add 12 or 2 points to the current session. After scoring, current session and origin thresholds are checked and `do_reaction` is called for session badness or origin failed-login badness.

State and persistence: updates in-memory `session_data_t.score` and may raise origin karma after a session reaction. No disk persistence; session state disappears when removed or on process restart.

Dependencies and integration: depends on audit rules in `rules/*.rules`, auparse normalization, `session.c`, `origin.c`, and `reactions.c`. The configured thresholds and reactions are from `ids_config.c`.

Risks: scoring depends on audit rule key strings staying exactly synchronized. `s->killed` is checked but this file never sets it, so repeated session reactions may occur unless another reaction path mutates it. Daemon or missing sessions are ignored.

Test signals: feed auparse events with keys `ids-recon`, `ids-archive`, `ids-mkexec`, and `ids-connections`; verify score increments and threshold-triggered reactions.
