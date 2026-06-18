# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_bio.c

## Summary
Threaded POSIX block I/O backend for rumpuser.

## Key Details
- Defines a fixed 128-entry circular queue protected by a mutex and condition variable.
- `dobio` executes `pread`/`pwrite`, optional write sync, error translation, and biodone callback invocation.
- A worker thread registers with the rump kernel as a new LWP before servicing queued I/O.
- `RUMP_THREADS=0` disables the worker thread and executes BIO synchronously.
- Queue producers block when the ring is full and signal the worker on enqueue.
- The callback is invoked while the rump kernel is scheduled, then the worker unschedules again.

## Notes
Initialization is lazy and protected by a double-checked `inited` flag under `biomtx`.
