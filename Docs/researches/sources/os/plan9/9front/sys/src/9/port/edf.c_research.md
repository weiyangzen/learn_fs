# File Research: sources/os/plan9/9front/sys/src/9/port/edf.c

Implements kernel earliest-deadline-first scheduling support. It manages EDF admission, release/deadline timers, runtime accounting, yield-to-next-period behavior, and a schedulability test over admitted processes.

`edfinit` allocates `Edf` state. `edfadmit` validates period/cost/deadline settings, runs `testschedulability`, marks the process admitted, synchronizes releases with same-period tasks where possible, and schedules immediate or future release. `edfready` decides whether a process is runnable now, should wait for release, or can continue best-effort with extra time.

`edfrun` arms deadline timers based on remaining slice and deadline. `edfrecord` charges runtime to EDF or extra time and forces deadline expiry when budget is exhausted. `edfyield` sleeps until the next release. `edfstop` expels a process and cancels timers.

The schedulability test simulates release/deadline events ordered by `testenq`, bounded by `Maxsteps`. Integration points include run queues, timer callbacks, process tracing, and process priority demotion to `PriExtra`.
