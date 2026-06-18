# File Research: sources/os/plan9/9front/sys/src/cmd/mk/run.c

Schedules and waits for recipe jobs with configurable parallelism.

Key behavior:
- Maintains a pending job list and an event table of running jobs keyed by slot/pid.
- `nproc()` reads `NPROC`, clamps to at least 1, and resizes event slots.
- `sched()` builds job environment, prints commands unless quiet/no-exec/touch, runs rc, or simulates/touches targets.
- `waitup()` handles completed children, rogue processes, errors, delete-on-error targets, keep-going mode, target updates, and scheduling more jobs.
- Tracks concurrency usage by running job count.

Important dependencies: `mk.h`, `buildenv`, `shprint`, `execsh`, `waitfor`, `update`, `delete`.

Notable risks:
- Unexpected child processes are saved in a side list and can later satisfy explicit waits.
- Error handling differs sharply under `-k`; failed targets become fake `BEINGMADE`.
