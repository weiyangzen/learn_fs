<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c -->
# sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c

**Purpose**
`aulastlog` reports each local user’s most recent successful login based on audit logs rather than traditional lastlog storage.

**Important APIs, Types, And Functions**
The main function uses libc password APIs `getpwent`/`endpwent`, auparse search APIs `ausearch_add_item`, `ausearch_set_stop`, `ausearch_next_event`, `auparse_get_timestamp`, `auparse_find_field`, and `auparse_get_field_int`, plus the local linked-list API.

**Control Flow**
Arguments accept `--stdin` and `--user`/`-u`. The program first builds a list of all passwd users or a single named user, failing if the requested user is unknown. It initializes auparse from stdin or system logs, adds search filters for `type = USER_LOGIN` and `res = success`, and scans matching events. For each event with an `auid`, it finds the user node and updates login time, hostname, and terminal. Finally it prints a fixed-width table with `**Never logged in**` for users with no matched event.

**State And Persistence**
State is the in-memory user list. It reads local passwd and audit logs but writes only stdout diagnostics/reporting.

**Dependencies And Integration Points**
It depends on auparse, audit log access, local account data, locale/time formatting, and the `aulastlog` list implementation.

**Risks**
The loop calls `ausearch_next_event` again at the end of each body, which advances an extra event and may skip matches depending on auparse semantics. The code only preserves the last matching record encountered, assuming log traversal order corresponds to increasing time. It has no root warning for log access failure.

**Test Signals**
No direct runtime test is registered in this subset; build and manual audit-log tests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/aulastlog.c -->
