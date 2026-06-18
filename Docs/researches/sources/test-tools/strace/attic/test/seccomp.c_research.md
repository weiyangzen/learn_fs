<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/seccomp.c -->
# sources/test-tools/strace/attic/test/seccomp.c

Purpose: seccomp-BPF reproducer that verifies denied syscalls return specified errno values and exercises strace seccomp/audit architecture decoding.

Important APIs/macros: maps compile architecture to `AUDIT_ARCH_*`; defines BPF helper macros for kill, deny, and allow rules. Static `filter[]` validates architecture, loads syscall number, allows `close`, `exit`, `exit_group`, denies `sync`, `setsid`, `getpid`, and `munlockall`, then kills everything else. `main` sets `PR_SET_NO_NEW_PRIVS`, installs `SECCOMP_MODE_FILTER`, and tests denied syscalls via raw `syscall`.

Control flow: after filter installation, only explicitly allowed syscalls can complete. Test failures trigger forbidden `close(-fail)` patterns.

State and persistence: seccomp state is process-local and irreversible. No files written.

Dependencies and integration: requires Linux seccomp, audit constants, BPF filter headers, and architecture support from preprocessor branches.

Risks: unsupported architectures fail compilation. The test closes stdio and uses `_exit`, making diagnostics sparse. Test signals: process should exit 0 when denied syscalls report expected errnos; strace should decode seccomp events and raw syscalls correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/seccomp.c -->
