# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify21.c

Purpose: checks the `fanotify_event_info_pidfd` record returned in `FAN_REPORT_PIDFD` mode, including valid pidfds, terminated-child pidfd errors, and read-only mount event-fd behavior with and without `FAN_REPORT_FD_ERROR`.

Important APIs/types/functions: `fanotify_init`, `fanotify_mark`, `fanotify_event_info_pidfd`, `pidfd_open`, `/proc/self/fdinfo`, `SAFE_FILE_LINES_SCANF`, `FAN_REPORT_FD_ERROR`, `FAN_NOPIDFD`, `FAN_EVENT_INFO_TYPE_PIDFD`, bind remounts with `MS_RDONLY`, and LTP `test_variants`.

Control flow: setup bind-mounts the test mount, optionally enables `FAN_REPORT_FD_ERROR`, creates the watched file, initializes a pidfd-reporting group, marks `FAN_OPEN`, and records fdinfo for a pidfd to self. Each case remounts rw or ro, generates an event in self or a child, reads queued events, validates pidfd info header fields, checks event fd error reporting, checks expected pidfd error for terminated children, and compares fdinfo for valid pidfds.

State/persistence behavior: state includes a bind mount toggled read-only/read-write, one fanotify queue, and dynamically allocated fdinfo snapshots. Event fd and pidfd descriptors are closed after inspection.

Dependencies/integration: requires root, mounted filesystem support for pidfd fanotify, `pidfd_open`, proc fdinfo fields, and optional `FAN_REPORT_FD_ERROR` support for variant 1.

Risks/test signals: sensitive to pid lifetime races and mount writeability semantics. Strong signals include header length/type checks, pid identity checks, fd error values, and fdinfo equality with the self pidfd baseline.
