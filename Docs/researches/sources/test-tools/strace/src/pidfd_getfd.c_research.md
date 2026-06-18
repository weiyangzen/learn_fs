<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_getfd.c -->
# sources/test-tools/strace/src/pidfd_getfd.c

Purpose: decodes `pidfd_getfd`.

Important APIs/types/functions: `SYS_FUNC(pidfd_getfd)`, `pidfd_get_pid`, `printfd`, and `printfd_pid`.

Control flow: prints pidfd, then tries to resolve the pidfd target pid so the target fd can be rendered in that process context; otherwise prints target fd numerically. Flags are printed as hex and the return value is fd-formatted.

State and persistence behavior: no state.

Dependencies and integration points: depends on pidfd-to-pid lookup and fd printing helpers; integrated as a syscall decoder.

Risks: target fd path rendering depends on resolving pidfd and `/proc` access. Flags currently have no symbolic table here.

Test signals: valid pidfd target resolution, invalid pidfd fallback, flags zero/nonzero, and returned fd formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pidfd_getfd.c -->
