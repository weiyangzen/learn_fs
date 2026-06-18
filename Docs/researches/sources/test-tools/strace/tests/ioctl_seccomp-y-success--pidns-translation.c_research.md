<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c

Purpose: seccomp wrapper combining pid namespace translation with the `-y` injected-success variant.

Important APIs/types/functions: Defines `PIDNS_TRANSLATION` and includes `ioctl_seccomp-y-success.c`, which itself enables `INJECT_RETVAL 1` and fd path printing.

Control flow: included base test runs after injection lock; output includes pidns leaders/suffixes and source fd path annotations in `SECCOMP_IOCTL_NOTIF_ADDFD`.

State and persistence behavior: local structs and controlled fds only; no real seccomp listener is required due to injection.

Dependencies/integration points: composes pidns translation, fd-path rendering, and injection in seccomp ioctl expected output.

Risks and test signals: expected text depends on `/proc/self/fd` availability and pidns harness. Passing output confirms combined annotations are placed correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation.c -->
