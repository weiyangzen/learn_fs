# sources/security-integrity/audit-userspace/audisp/plugins/syslog/audisp-syslog.c

Purpose: reads audit records from audisp stdin and writes them to syslog, optionally interpreting fields through auparse.

Important APIs and data: local state includes stop/hup flags, syslog priority, interpret mode, and reusable record buffer. Key functions are `init_syslog`, `write_syslog`, and `main`.

Control flow: command-line args select syslog priority, facility, and optional `interpret`. Main installs signal handlers, drops capabilities, then waits on stdin with `select` and drains auplugin lines. Non-interpreted mode replaces the audit interpretation separator with a space and syslogs raw text. Interpreted mode creates an auparse buffer, drops EOE-like empty records, formats interpreted `name=value` fields, and adds a human-readable timestamp header.

State and persistence: only in-memory buffer and flags; output persistence is delegated to syslog.

Dependencies and integration: depends on auplugin line input, auparse interpretation helpers, libaudit constants, syslog facilities, and dispatcher `syslog.conf` args.

Risks: interpreted formatting truncates when near `MAX_AUDIT_MESSAGE_LENGTH - 128`. `reload_config` only clears hup and does not reread args. Signal termination honors only parent SIGTERM.

Test signals: feed raw and interpreted audit records, EOE records, unknown args, facility/priority args, HUP/TERM behavior, and separator replacement.
