<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y.c

Purpose: fd-path (`-y`) variant of seccomp ioctl decoding. It enables path printing and skips when `/proc/self/fd/` is unavailable.

Important APIs/types/functions: Defines `PRINT_PATHS 1`, `SKIP_IF_PROC_IS_UNAVAILABLE`, and includes `ioctl_seccomp.c`. Inherited key structs are `seccomp_notif`, `seccomp_notif_resp`, and `seccomp_notif_addfd`.

Control flow: base seccomp test runs normally but `PATH_FMT` includes `<%s>` for `srcfd` fields, so controlled fds 0 and 42 print `/dev/null` and `/dev/zero` in addfd cases.

State and persistence behavior: opens and duplicates `/dev/null` and `/dev/zero` to deterministic fds; otherwise local structs only.

Dependencies/integration points: integrates seccomp ioctl decoding with strace fd-path annotation behavior.

Risks and test signals: depends on `/proc/self/fd` and deterministic fd duplication. Passing output confirms `-y` paths are included only where expected.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y.c -->
