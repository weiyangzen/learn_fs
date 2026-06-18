# sources/test-tools/strace/src/syslog.c

Purpose: decoder for `syslog`/`klogctl` actions.

Important APIs/types/functions: `SYS_FUNC(syslog)`, `syslog_action_type`, `syslog_console_levels`, `printstrn`, and `syserror`.

Control flow: on entry always prints action type. Actions that ignore `bufp` and `len` finish immediately. Read actions defer buffer printing until exit and print returned bytes only on success. Console-level action interprets `len` as log level. Unknown/default actions print raw buffer address and decimal length.

State and persistence behavior: stateless; reads output buffer only after successful read-like actions.

Dependencies and integration points: syscall table maps syslog here; generated xlats provide action/level names.

Risks: action-specific argument meaning is irregular. For failed read actions it must not read tracee buffer.

Test signals: close/open/clear, size queries, read/read_all/read_clear success/failure, console-level names, unknown action, and buffer truncation by return value.
