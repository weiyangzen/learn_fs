# sources/test-tools/stress-ng/core-out-of-memory.c

Purpose: manages OOM-killer adjustment and provides a retrying child-process wrapper for stressors expected to exhaust memory.

Important APIs/functions: `stress_process_oomed`, `stress_set_oom_adjustment`, and `stress_oomable_child`, with Linux, FreeBSD, and stub variants.

Control flow: Linux detection scans `/dev/kmsg` for OOM messages mentioning the child PID. Adjustment writes `/proc/self/oom_score_adj`, falling back to `/proc/self/oom_adj`. The child wrapper optionally bypasses for `--oom-no-child`; otherwise it forks, marks the child OOM-killable, optionally drops capabilities, invokes the callback, and the parent restarts on OOM SIGKILL, SIGSEGV, or SIGBUS unless `--oomable` accepts OOM success.

State/persistence: mutates process OOM score/protection, child lifecycle, `args->stats->s_pid.oomable_child`, and `args->bogo.possibly_oom_killed`; can clean stressor temp directories.

Dependencies/integration: global flags/timeouts, signal helpers, capability dropping, process state reporting, kill helpers, filesystem cleanup, and platform OOM APIs.

Risks: `/dev/kmsg` may be unreadable; OOM attribution is heuristic; fork under pressure can loop; changing OOM scores requires permissions; callbacks must be fork-safe.

Test signals: Linux privileged/unprivileged runs, `--oomable`, `--oom-no-child`, `--no-oom-adjust`, child SIGBUS/SIGSEGV restart, wait interruption escalation, timeout handling, and FreeBSD/stub builds.
