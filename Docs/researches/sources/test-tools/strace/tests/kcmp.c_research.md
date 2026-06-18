<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp.c -->
# sources/test-tools/strace/tests/kcmp.c

Purpose: Tests decoding of the `kcmp` syscall, including PID arguments, comparison types, fd arguments, and `KCMP_EPOLL_TFD` pointer decoding.

Important APIs/types/functions: Uses `syscall(__NR_kcmp)`, `open`, `dup2`, `close`, `struct kcmp_epoll_slot`, `PIDNS_TEST_INIT`, `pidns_pid2str`, `printpidfd`, and `do_kcmp`.

Control flow: Opens `/dev/null` and `/dev/zero` into stable fds 23 and 42, closes fd 0, runs invalid type/pid cases, tests `KCMP_FILE` with bogus and real fds, prints all simple `KCMP_*` types, and tests `KCMP_EPOLL_TFD` with NULL/faulting pointers plus three filled slot structures.

State/persistence behavior: Process-local file descriptors are opened and duplicated. No persistent filesystem state is modified.

Dependencies: Requires `__NR_kcmp`, Linux `kcmp.h`, pid namespace helpers, and optionally `/proc/self/fd/` for verbose fd-path wrappers.

Integration points: Validates strace's kcmp decoder, fd path annotation in verbose mode, pid namespace translation, optional pointer decoding for epoll slots, and unknown-type fallback.

Risks: Kernel permission restrictions can change errno. `/dev/null`, `/dev/zero`, and `/proc/self/fd/` availability affect wrapper variants.

Test signals: Output includes invalid fallback, all known comparison type names, decoded fd paths when verbose wrapper is used, epoll slot structures, pidns prefixes, and final exit.

Source read signal: complete file read for this research pass; file size 209 line(s), 5140 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp.c -->
