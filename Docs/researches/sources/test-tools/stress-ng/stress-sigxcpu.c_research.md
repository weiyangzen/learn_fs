# sources/test-tools/stress-ng/stress-sigxcpu.c

Purpose: implements the `sigxcpu` stressor, repeatedly lowering CPU or realtime runtime limits to provoke SIGXCPU and verify delivery under resource-limit pressure.

Important APIs/types/functions: `stress_sigxcpu_handler`, `stress_sigxcpu_cpu_usage`, `stress_sigxcpu`, `getrlimit`, `setrlimit`, `RLIMIT_CPU`, `RLIMIT_RTTIME`, `SIGXCPU`, `getrusage`, and `shim_sched_yield`.

Control flow: the worker installs a SIGXCPU handler, snapshots CPU and realtime limits, synchronizes start, records initial CPU usage, then loops setting soft limits to zero and yielding. The handler increments bogo ops. On exit it ignores SIGXCPU and, in verify mode, reports failure if more than about 10 seconds of CPU runtime elapsed without any bogo increments.

State and persistence behavior: state is process resource limits and a global args pointer. The code snapshots limits but does not visibly restore them in this file, so the stressor relies on worker process lifetime/isolation for cleanup.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify, and unimplemented without SIGXCPU plus at least one relevant rlimit. It depends on rusage support for verification when available.

Risks and test signals: manipulating rlimits can affect the running worker and may fail under container policy. There is a likely typo in the `RLIMIT_RTTIME` snapshot path using `getrlimit(RLIMIT_CPU, &limit_rttime)`, which should be reviewed. Test signals are SIGXCPU bogo increments, `setrlimit` failures, and verify-mode no-signal reports.
