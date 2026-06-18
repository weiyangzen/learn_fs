# File Research: sources/os/bsd/openbsd-src/sys/sys/proc.h

Defines OpenBSD process and thread core structures. It includes sessions, process groups, time-usage accounting, shared `struct process`, per-thread `struct proc`, process/thread flags, status values, PID/TID limits, fork/exit flags, global process lists, pools, lookup helpers, scheduler/process lifecycle APIs, credential refresh, single-threading controls, condition variables, CPU sets, and time-usage helpers.

`struct process` holds shared identity, credentials, fd table, vmspace, parent/child/group/session relationships, signal state, timers, rusage, pledge/unveil state, pinsyscall data, limits, and process metadata. `struct proc` holds per-thread run queue state, scheduler state, signal masks, credentials, profiling state, machine-dependent state, and debug/core fields.

Filesystem relevance includes current process credentials, fd tables, root/cwd interactions through other structures, pledge/unveil enforcement, syncer process declaration, and resource accounting.
