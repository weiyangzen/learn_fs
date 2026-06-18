# sources/test-tools/strace/src/printsiginfo.c

Purpose: Decodes `siginfo_t` instances and arrays into signal-source, code, and signal-specific payload fields.

Important APIs/types/functions: `printsiginfo`, `printsiginfo_at`, and `print_siginfo_array`; helpers include `printsigsource`, `printsigval`, `print_si_code`, and `print_si_info`.

Control flow: prints `si_signo` and xlat-backed `si_code`, skips further details for `SI_NOINFO`, then branches on user-originated vs kernel-originated signals and by signal number. It decodes process/uid sources, timers, SIGIO band/fd, SIGCHLD status/times, fault addresses, SIGTRAP perf metadata, SIGSYS syscall/arch, and optional architecture fields guarded by feature macros.

State and persistence: stateless; all `siginfo_t` data is fetched from tracee memory or array iteration buffers.

Dependencies/integration: uses MPERS, `<signal.h>`, audit arch xlat, many signal code xlat tables, `printsignal`, fd/pid/id helpers, and ptrace/signal syscall decoders.

Risks: `siginfo_t` is union-heavy and libc/kernel fields vary by architecture and feature macros. Wrong `si_code` classification can print invalid union members. Signal-code xlat lookup must prefer generic codes but fall back to signal-specific tables.

Test signals: `rt_sigqueueinfo`, `waitid`, ptrace get/set siginfo, seccomp SIGSYS, SIGCHLD status, SIGSEGV/SIGBUS address cases, and xlat modes.
