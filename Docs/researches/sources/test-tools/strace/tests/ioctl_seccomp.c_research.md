<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp.c -->
# sources/test-tools/strace/tests/ioctl_seccomp.c

Purpose: comprehensive decoder test for seccomp user notification ioctls: receive, send, id-valid, addfd, set-flags, unknown commands, pid namespace translation, fd path output, and injected success.

Important APIs/types/functions: Uses `sys_ioctl`, `PIDNS_TEST_INIT`, `pidns_print_leader`, `pidns_pid2str`, `linux/seccomp.h`, `struct seccomp_notif`, `seccomp_notif_resp`, `seccomp_notif_addfd`, `SECCOMP_IOCTL_NOTIF_RECV`, `SEND`, `ID_VALID`, `ADDFD`, `SET_FLAGS`, audit arch xlat tables, and fd/path macros.

Control flow: prints a synchronized starting marker, optionally locks onto injected success, sweeps unknown seccomp ioctl directions/sizes, then tests `NOTIF_RECV` with NULL, bad pointer, zeroed and populated notifications including syscall args and audit arch variants. It tests `NOTIF_SEND` responses, `NOTIF_ID_VALID` and wrong-direction command, sets up deterministic fds for `/dev/null` and `/dev/zero`, tests `NOTIF_ADDFD` with flags and fd paths, and finishes with `NOTIF_SET_FLAGS`.

State and persistence behavior: process-local notification structs plus fd table manipulation for descriptors 0 and 42. No real seccomp listener state is required on invalid fd; injection simulates success.

Dependencies/integration points: depends on seccomp UAPI, audit arch definitions, pid namespace helpers, fd path availability, kernel fcntl flags, xlat modes, and syscall injection.

Risks and test signals: many formatting dimensions interact: xlat mode, pidns translation, fd paths, injection, arch-specific syscall numbers, and `/proc` availability. Passing output confirms strace correctly decodes nested seccomp notification structs, signed errors, flags, fds, PIDs, syscall metadata, and unknown command fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp.c -->
