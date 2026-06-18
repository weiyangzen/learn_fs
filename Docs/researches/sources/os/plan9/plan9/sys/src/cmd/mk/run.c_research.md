# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/run.c

Schedules and monitors recipe jobs.

Key data:
- `events[]` maps process slots to active jobs.
- `jobs` queue stores pending jobs.
- `Process` list stores unexpected child statuses.
- `nproclimit` is controlled by `NPROC`.

Key functions:
- `run()` appends a job and schedules if slots are available.
- `sched()` builds environment, prints recipe, handles `-n`/`-t`, or executes shell command.
- `waitup()` waits for children, handles errors, updates targets, schedules more jobs.
- `nproc()`, `nextslot()`, `pidslot()` manage process slots.
- `killchildren()` posts notes to children on interrupt.
- `usage()` / `prusage()` track time spent at each concurrency level.

Behavior notes:
- Recipe failures delete targets marked `DELETE`.
- `-k` records errors and continues; otherwise exits.
- `NOMINUSE` suppresses `rc -e` behavior.
