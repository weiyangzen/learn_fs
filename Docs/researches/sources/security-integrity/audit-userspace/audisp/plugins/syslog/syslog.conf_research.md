# sources/security-integrity/audit-userspace/audisp/plugins/syslog/syslog.conf

Purpose: dispatcher registration for forwarding audit events to syslog.

Important APIs and data: disabled by default, path `/sbin/audisp-syslog`, type `always`, args `LOG_INFO`, and string format. Comments document valid priority/facility arguments and optional behavior.

Control flow: audit dispatcher passes args to `audisp-syslog`, which parses them in `init_syslog`.

State and persistence: persistent plugin configuration.

Dependencies and integration: relies on syslog plugin accepting the configured priority token.

Risks: disabled by default; invalid args cause plugin startup failure.

Test signals: dispatcher config parse and syslog plugin arg parsing.
