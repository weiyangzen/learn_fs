# sources/test-tools/fio/engines/solarisaio.c

## Purpose
`solarisaio.c` implements fio's native Solaris asynchronous I/O engine using `aioread`, `aiowrite`, and `aiowait` from `<sys/asynch.h>`.

## Important APIs, Types, And Functions
`struct solarisaio_data` contains an array of completed `io_u` pointers, a pending completion count, an in-flight count, and a maximum depth capped to `MAXASYNCHIO`. `fio_solarisaio_prep()` initializes `io_u->resultp` and attaches engine data. `wait_for_event()` calls `aiowait`, converts Solaris `aio_result_t` back to the enclosing `io_u`, sets residual/error state, stores it in the event array, and decrements in-flight count. Queueing uses `aioread`/`aiowrite`; sync directions use `fsync`/`fdatasync`.

## Control Flow
`.init` allocates state and caps depth to the OS limit. `.prep` marks each request in progress. `.queue` refuses sync operations while async requests are outstanding, refuses more async work once `nr == max_depth`, and submits reads or writes at `io_u->offset`. `.getevents` converts fio's timeout to `timeval`, repeatedly calls `wait_for_event()` until `min` completions are pending, then returns and clears the pending count. `.event` indexes the completion array.

## State And Persistence
State is per-thread and volatile. Data persists only through the target file descriptors opened by generic fio file handling. Optional `USE_SIGNAL_COMPLETIONS` installs a SIGIO handler that calls `wait_for_event(NULL)`.

## Dependencies And Integration Points
The engine depends on Solaris-specific async I/O APIs, generic fio file open/close/size hooks, fio barriers, and optional signal delivery. It registers a built-in engine named `solarisaio`.

## Risks
The pending-event counter is manipulated without a lock; comments assume integer operations are atomic, but signal-driven completion mode requires only a write barrier between event storage and count update. Timeout behavior is weak: if `min` is nonzero and no events arrive, `getevents` can repeatedly call `aiowait` with the same timeout. The signal handler calls nontrivial code, including logging/exit paths in error cases.

## Test Signals
Testing requires Solaris or compatible APIs. Useful cases are depth capping, read/write completion residuals, sync refusal while async I/O is in flight, timeout behavior, and signal-completion builds.
