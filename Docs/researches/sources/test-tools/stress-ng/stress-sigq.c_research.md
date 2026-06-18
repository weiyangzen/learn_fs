# sources/test-tools/stress-ng/stress-sigq.c

Purpose: implements the `sigq` stressor, sending queued SIGUSR1 signals with payloads to a child that consumes them through `sigwaitinfo` and `sigtimedwait`.

Important APIs/types/functions: `stress_sigqhandler`, `stress_sigq_chld_handler`, optional `shim_rt_sigqueueinfo`, `stress_sigq`, `sigqueue`, `sigwaitinfo`, `sigtimedwait`, `sigprocmask`, `sigaction`, `SA_SIGINFO`, `fork`, and CPU affinity helpers.

Control flow: the parent installs SIGCHLD and SIGUSR1 handlers, synchronizes start, forks a child, and the child blocks SIGUSR1 then alternates between `sigwaitinfo` and `sigtimedwait`, verifying the queued integer payload and signal number. The parent repeatedly sends the configured payload with `sigqueue`, optionally probes Linux `rt_sigqueueinfo` invalid cases, increments bogo ops, sends a zero-valued termination notice, and reaps the child.

State and persistence behavior: state is queued signal payloads and a volatile `handled_sigchld` flag that can stop the run if the child exits. No durable resources are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS | CLASS_IPC`, always verify, and unimplemented without sigqueue/sigwaitinfo/SA_SIGINFO. It integrates with CPU affinity and raw syscall guards on Linux.

Risks and test signals: signal queue saturation, child early exit, payload corruption, and platform-specific realtime signal semantics are key risks. Failures include unexpected payload/signum, fork failure, or child exit with failure.
