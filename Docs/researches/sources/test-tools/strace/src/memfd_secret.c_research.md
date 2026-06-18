<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/memfd_secret.c -->
# sources/test-tools/strace/src/memfd_secret.c

Purpose: decodes `memfd_secret` flags.
Important APIs/types/functions: `SYS_FUNC(memfd_secret)`, `kernel_fcntl.h`, and `memfd_secret_flags`.
Control flow: prints symbolic flags for the single argument and marks the return as a file descriptor. State and persistence behavior: none.
Dependencies and integration points: syscall table and fd-return handling. Risks: new flags need xlat updates; unknown bits should remain visible. Test signals: zero, known, and unknown memfd_secret flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/memfd_secret.c -->
