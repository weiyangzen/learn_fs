<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c

Purpose: combined seccomp variant enabling fd path printing (`-y`), injected success, pid namespace translation, and abbreviated xlat output.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `ioctl_seccomp-y-success--pidns-translation.c`, which layers `PIDNS_TRANSLATION`, `INJECT_RETVAL 1`, and `PRINT_PATHS`.

Control flow: base seccomp matrix runs after injection lock with pidns leaders, fd paths for addfd source descriptors, and abbreviated xlat strings.

State and persistence behavior: local seccomp structs plus controlled `/dev/null` and `/dev/zero` fds.

Dependencies/integration points: exercises combined strace options: injection, `-y`, pidns translation, and `-X abbrev`.

Risks and test signals: compounded formatting modes make expected output brittle. Passing output confirms these options compose correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xabbrev.c -->
