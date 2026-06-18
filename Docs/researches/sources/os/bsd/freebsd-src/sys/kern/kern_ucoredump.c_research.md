# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ucoredump.c

## Purpose
Coordinates user process termination by fatal signal and dispatches user core dumps to registered coredumper backends.

## Key Interfaces
- `coredumper_register()` and `coredumper_unregister()` manage registered coredump handlers.
- `sigexit()` forces the current process to terminate with a signal, optionally generating a core dump and logging the exit.
- Internal `coredump()` applies policy checks, selects the best coredumper, and invokes its handler.
- Sysctls control signal-exit logging, setuid/setgid core dumps, coredump enablement, compression type, and compression level.

## State And Locking
Coredumpers are kept in an `SLIST` protected by `coredump_rmlock`. Each coredumper has a `blockcount` reference count so unregister waits until in-progress dumps using that backend finish. Process locking is required on entry to `sigexit()` and `coredump()`, but backend coredump handling drops the process lock.

## Control Flow
`sigexit()` marks the process as exiting, updates accounting flags, decides whether signal exits should be logged, single-threads the process for coherent register/thread-list state, stores the fatal signal, and calls `coredump()`. `coredump()` rejects dumps disabled by sysctl, setuid policy, trace-disable state, zero resource limit, or RACCT exhaustion. It then scans registered dumpers, prefers the highest nonnegative probe priority, takes a reference, drops the rmlock, calls the backend's `cd_handle(td, limit)`, and releases the reference. `sigexit()` converts coredump success into `WCOREFLAG`, logs the outcome, and exits through `kern_exit()`.

## Integration Notes
Integrates with signal semantics, process single-threading, accounting, RACCT/resource limits, jail IDs, credentials, syslog, compressor availability, and backend-specific core dump modules. The file assumes a vnode coredumper is always registered.

## Risks
Core dumping depends on successfully single-threading the process; a competing single-thread operation can suppress the dump. The coredumper selection path dereferences the selected backend after scanning, so the built-in vnode dumper assumption is significant. Policy errors are mapped to user-facing log strings, and backend handlers must return with the process lock dropped as expected.
