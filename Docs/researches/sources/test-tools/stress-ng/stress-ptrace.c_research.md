# sources/test-tools/stress-ng/stress-ptrace.c research

Purpose: implements `ptrace`, an OS stressor that traces a child process at syscall entry/exit boundaries and periodically exercises invalid ptrace requests.

Important APIs, types, and functions: `stress_syscall_wait()` drives `PTRACE_SYSCALL`, waits for the tracee, and detects syscall stops through `PTRACE_O_TRACESYSGOOD`. `stress_ptrace()` forks the tracee, configures ptrace options, loops tracing syscalls, and kills/reaps the child on exit.

Control flow: after synchronization, the parent forks. The child applies scheduler settings, calls `PTRACE_TRACEME`, stops itself with `SIGSTOP`, then repeatedly issues simple syscalls such as `getppid`, IDs, and `time`. The parent waits for the stop, sets ptrace options, then repeatedly resumes and waits for syscall stops. Every 512 iterations it calls ptrace with an invalid request and an invalid PID to exercise error paths. Termination kills and waits for the tracee.

State and persistence: only transient child process state and kernel tracing state exist. There are no files or persistent settings.

Dependencies and integration: gated by `HAVE_PTRACE`; uses fork/wait/kill stress-ng helpers, `stress_redo_fork`, scheduler application, and standard wait status macros. It is classified as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: systems with Yama, seccomp, containers, or existing tracers may reject ptrace. The stressor treats `ESRCH`, `EPERM`, and `EACCES` as skip-like traceability failures in several paths. Missing or delayed wait statuses can break tracing, so wait error handling is central.

Test signals: successful bogo increments per syscall stop, skip message when child cannot be traced, invalid ptrace calls not crashing the run, and reliable child cleanup indicate expected behavior.
