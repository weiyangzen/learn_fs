# sources/user-network-fs/s3fs-fuse/src/sighandlers.h

Purpose: declares the `S3fsSignals` singleton responsible for installing and coordinating s3fs runtime signal behavior.

Important APIs and types: public `Initialize()` forces singleton creation, and `SetUsr1Handler(const char* path)` enables cache-check handling before initialization. Private/protected handlers and helpers cover SIGUSR1, SIGUSR2, SIGHUP, cache worker management, semaphore wakeups, and teardown.

Control flow: callers configure SIGUSR1 output first, then call `Initialize`. Signal handlers are static because they are registered with `sigaction`; instance state holds the worker resources.

State and persistence: static `enableUsr1` plus owned `std::thread` and `Semaphore`. No persistent storage beyond logs/cache-check output.

Dependencies and integration points: includes `psemaphore.h`; implementation integrates with `FdManager` and `S3fsLog`.

Risks: singleton construction order matters because `SetUsr1Handler` only toggles state and output; if called after `Initialize`, the SIGUSR1 thread will not be started by the constructor. Plain static bool is used across threads/signals.

Test signals: startup-order tests for setting SIGUSR1 before/after initialization, handler registration failures, and clean destruction of the worker thread.
