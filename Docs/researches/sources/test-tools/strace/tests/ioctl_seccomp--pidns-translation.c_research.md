<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c

Purpose: pid-namespace translation variant for seccomp user notification ioctl decoding. It defines `PIDNS_TRANSLATION` and includes `ioctl_seccomp.c`.

Important APIs/types/functions: Inherits `SECCOMP_IOCTL_NOTIF_*`, `struct seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, and pidns helper printing from the base file.

Control flow: base seccomp matrix runs with pidns leader output and translated PID suffixes for notification `pid` fields.

State and persistence behavior: transient local structs and opened `/dev/null`/`/dev/zero` fds only.

Dependencies/integration points: integrates pid namespace translation with seccomp ioctl decoder output.

Risks and test signals: pid namespace harness affects expected prefixes and pid annotations. Passing output confirms seccomp notification pids are translated in the right fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp--pidns-translation.c -->
