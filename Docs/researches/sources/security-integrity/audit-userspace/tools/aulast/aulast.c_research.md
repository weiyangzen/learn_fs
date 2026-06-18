<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast.c -->
# sources/security-integrity/audit-userspace/tools/aulast/aulast.c

**Purpose**
`aulast` is a `last`-style command that reconstructs login sessions from Linux audit records instead of traditional wtmp data. It reports successful sessions by default and failed login attempts with `--bad`.

**Important APIs, Types, And Functions**
Key functions are `report_session`, `extract_record`, `create_new_session`, `update_session_login`, `update_session_logout`, `process_bootup`, `process_kernel`, `process_shutdown`, and `main`. It uses auparse APIs such as `auparse_init`, `auparse_next_event`, `auparse_get_type`, `auparse_find_field`, `auparse_get_field_int`, `auparse_interpret_field`, `auparse_get_time`, and `auparse_get_serial`.

**Control Flow**
`main` parses `--bad`, `--debug`, `--stdin`, `--proof`, `--extract`, `-f`, `--user`, and `--tty`; initializes auparse from a file, stdin, or system logs; then iterates events. `AUDIT_LOGIN` creates a preliminary session from auid/pid/session, closing a previous same-session entry as `GONE`. `AUDIT_USER_LOGIN` fills terminal/host/result details or immediately reports failed logins when requested. `AUDIT_USER_END` closes and reports matching sessions. Boot records mark open reboot/session entries as `CRASH` or `DOWN`, clear the list, and start a reboot record; shutdown closes the reboot record. At EOF, remaining sessions are reported.

**State And Persistence**
State is the process-local global `llist l`, optional extraction file `aulast.log`, cached kernel string, and command options. Output is stdout plus optional extracted raw records; no database is written.

**Dependencies And Integration Points**
It integrates with libaudit record constants, auparse log readers, the local linked list, libc locale/time functions, and root-readable audit logs.

**Risks**
Argument parsing increments indexes without consistently checking for missing option values for `-f`, `--user`, and `--tty`. Session correlation depends on audit fields being present and on one-record events. The linear list can be inefficient on large logs, and string duplication failures are not always checked.

**Test Signals**
The list library has direct tests, but this full parser/reporting flow is not directly covered in this subset beyond build/link coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/aulast.c -->
