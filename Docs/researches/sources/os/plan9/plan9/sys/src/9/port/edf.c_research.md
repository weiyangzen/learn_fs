# File Research: sources/os/plan9/plan9/sys/src/9/port/edf.c

Purpose: Earliest Deadline First scheduling support for Plan 9 processes with admitted real-time parameters.

Key logic:
- `edfinit` allocates per-process `Edf` state and installs time formatting.
- `edfadmit` validates period/cost/deadline, runs schedulability testing, marks the process admitted, synchronizes release time with same-period admitted tasks when possible, and schedules release/deadline timers.
- `release`, `releaseintr`, and `deadlineintr` manage periodic/sporadic releases, deadlines, rescheduling, and wakeups.
- `edfrun` arms a timer for the earlier of deadline or remaining CPU slice.
- `edfrecord` accounts used time against EDF or extra time and forces deadline when slice is exhausted.
- `edfready` inserts admitted processes into `runq[PriEdf]` ordered by earliest deadline or delays them until release.
- `edfyield` sleeps until the next release.
- `edfstop` expels a process and deletes timers.
- `testschedulability` simulates release/deadline events up to `Maxsteps`.

Dependencies and integration:
- Uses kernel `Proc`, `Timer`, run queues, trace hooks, scheduler state, `µs()`, `todge`t, and `edf.h`.

Risks and notes:
- Time is tracked in low-order microseconds, so wrap behavior is implicit.
- Schedulability testing is bounded and can return “probably not schedulable”.
- Locking is split between `edfschedlock` for admission parameters and `thelock` for runtime EDF state.
