# sources/test-tools/stress-ng/stress-sigfd.c

Purpose: implements the Linux-style `sigfd` stressor, blocking a real-time signal, receiving it through `signalfd`, and verifying signalfd read records while a child queues signals.

Important APIs/types/functions: `stress_sigfd`, optional `shim_signalfd4`, `signalfd`, `sigprocmask`, `sigqueue`, `struct signalfd_siginfo`, `read`, `stress_fs_fdinfo_read`, `stress_affinity_change_cpu`, `stress_kill_pid_wait`, and SIGRTMIN.

Control flow: the parent blocks SIGRTMIN, exercises invalid `signalfd` calls, opens a real signalfd, synchronizes start, forks a child on the same CPU, and the child loops `sigqueue` to the parent with incrementing integer values. The parent reads signalfd records, optionally verifies the signal number, periodically reads `/proc` fdinfo, increments bogo ops, and kills the child on exit.

State and persistence behavior: signal mask changes are process-local; the signalfd is a transient fd closed at exit. Child state is only queued signal value progression.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify, and unimplemented without signalfd/sigqueue support. It integrates with CPU affinity and fdinfo helpers.

Risks and test signals: risks include SIGRTMIN availability, signal queue saturation (`EAGAIN` tolerated in child), incorrect mask setup, short reads, and leaked child/fd state. Verification catches unexpected signal numbers.
