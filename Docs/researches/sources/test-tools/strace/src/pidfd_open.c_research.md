<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_open.c -->
# sources/test-tools/strace/src/pidfd_open.c

Purpose: decodes `pidfd_open`.

Important APIs/types/functions: `SYS_FUNC(pidfd_open)` and `pidfd_open_flags`.

Control flow: prints the target pid as a TGID with namespace translation support, prints flags symbolically, and marks the return value as an fd.

State and persistence behavior: no state.

Dependencies and integration points: uses pid printers, `kernel_fcntl.h`, and generated pidfd flag xlats.

Risks: new pidfd flags require xlat updates. PID printing depends on namespace translation settings.

Test signals: valid pid, pid zero/negative error cases, known and unknown flags, and fd return formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_open.c -->
