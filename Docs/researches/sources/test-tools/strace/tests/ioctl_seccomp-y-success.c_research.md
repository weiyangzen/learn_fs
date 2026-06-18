<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success.c

Purpose: injected-success wrapper for the fd-path (`-y`) seccomp ioctl test.

Important APIs/types/functions: Defines `INJECT_RETVAL 1` and includes `ioctl_seccomp-y.c`, which sets `PRINT_PATHS` and `/proc/self/fd` availability checks.

Control flow: after injection lock, the base seccomp test runs with successful return strings and fd path annotations in addfd output.

State and persistence behavior: local seccomp structs and controlled descriptors; injection simulates seccomp listener success.

Dependencies/integration points: combines syscall injection and strace fd-path output.

Risks and test signals: requires `/proc/self/fd` and injection args. Passing output confirms success-path seccomp decoding with `srcfd=<path>` annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success.c -->
