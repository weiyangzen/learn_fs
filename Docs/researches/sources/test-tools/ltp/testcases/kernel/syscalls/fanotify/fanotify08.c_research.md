# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify08.c

Purpose: Sanity-checks that `FAN_CLOEXEC` maps to `FD_CLOEXEC` on a fanotify descriptor.

Important APIs/types/functions: `fanotify_init`, `FAN_CLOEXEC`, `SAFE_FCNTL(F_GETFD)`, `FD_CLOEXEC`, and two test rows.

Control flow: One row creates a group without `FAN_CLOEXEC` and expects the bit clear; the other creates one with `FAN_CLOEXEC` and expects the bit set.

State and persistence behavior: State is file descriptor close-on-exec metadata only.

Dependencies and integration points: Requires root and fanotify header support; no filesystem marks are created.

Risks and test signals: Failures are direct descriptor flag mismatches, pointing to init flag handling.
