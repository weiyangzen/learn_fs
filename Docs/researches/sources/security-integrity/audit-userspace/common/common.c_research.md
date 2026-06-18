<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.c -->
# sources/security-integrity/audit-userspace/common/common.c

Purpose: shared utility implementations for audit userspace components.

Important APIs and functions: `audit_is_last_record` classifies event-ending audit record types; `write_to_console` writes formatted messages to `/dev/console`; `wall_message` broadcasts to active utmpx user terminals with nonblocking partial-write handling; `time_string_to_seconds` parses numeric durations with units; `get_progname` caches basename from `/proc/self/exe`; `change_runlevel` forks and execs `/sbin/init` with target level and reports failures through `audit_msg`.

Control flow and state: static cached `progname` persists after first lookup. `SINGLE` and `HALT` are global string constants. `change_runlevel` parent waits for child; child unblocks signals and execs init.

Dependencies and integration: uses libaudit constants, syslog, utmpx, procfs, signals, wait, and private `audit_msg`. Event assembly elsewhere depends on `audit_is_last_record`.

Risks and test signals: risks include stale audit type ranges, blocking or failed terminal writes, unsafe assumptions about `/sbin/init`, static buffer truncation, and time-unit overflow. Coverage is mostly indirect through daemon behavior and event parsing tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.c -->
