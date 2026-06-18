# sources/test-tools/strace/src/ptrace.h

Purpose: Provides ptrace constants, compatibility definitions, and declarations needed by ptrace-related decoders.

Important APIs/types/functions: defines fallback `PTRACE_*` values and `struct_ptrace_syscall_info` compatibility shape where system headers lack it; exposes capability flags and printer/probe declarations used by `ptrace.c` and `ptrace_syscall_info.c`.

Control flow: compile-time only; preprocessor guards adapt to kernel/libc header support and architecture availability.

State and persistence: declares global support booleans for syscall-info APIs but does not mutate them itself.

Dependencies/integration: included by ptrace syscall decoder, syscall-info feature probe, and architecture code needing stable constants independent of host headers.

Risks: fallback constants must match Linux UAPI. Structure layout compatibility is high risk because printing and feature probes use `offsetof`/`offsetofend` for partial fetches.

Test signals: build against old and new kernel headers, run syscall-info and classic ptrace tests, and verify structure sizes in CI across architectures.
