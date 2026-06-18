# sources/user-network-fs/s3fs-fuse/src/sighandlers.cpp

Purpose: implements process signal handling for runtime cache checks, log-level bumping, and logfile reopening.

Important APIs and functions: `S3fsSignals::SetUsr1Handler` enables SIGUSR1 cache checking and configures output. `HandlerUSR1` wakes a worker thread. `CheckCacheWorker` drains queued signals and calls `FdManager::CheckAllCache`. `HandlerUSR2` bumps logging level. `InitUsr2Handler` and `InitHupHandler` register handlers. `HandlerHUP` reopens the log file. Constructor/destructor initialize and tear down handlers, and `WakeupUsr1Thread` releases the semaphore.

Control flow: setup optionally enables SIGUSR1 only if the platform supports `SEEK_DATA`/`SEEK_HOLE` and cache output can be configured. The singleton constructor installs SIGUSR2 and SIGHUP unconditionally and starts the SIGUSR1 worker if enabled. SIGUSR1 itself only releases a semaphore; the worker performs cache scanning outside the handler context. Destruction disables the worker, releases it, joins, and resets resources.

State and persistence: static `enableUsr1` gates the worker and handler behavior. Instance state owns the worker thread and semaphore. Side effects include signal-handler registration, cache-check output, log-level changes, and logfile reopening.

Dependencies and integration points: depends on `Semaphore`, `S3fsLog`, and `FdManager`. Initialization is exposed through `S3fsSignals::Initialize()` in the header and should occur during process startup.

Risks: SIGUSR2 and SIGHUP handlers call non-async-signal-safe C++/logging code directly. `enableUsr1` is a plain bool shared between signal handlers, main thread, and worker thread. Handler registration does not preserve previous handlers. Destructor joins only when SIGUSR1 was enabled.

Test signals: signal-integration tests for SIGUSR1 cache checks, coalescing queued semaphore releases, SIGUSR2 log-level cycling, SIGHUP logfile reopen, unsupported SEEK_DATA/SEEK_HOLE behavior, and thread teardown under repeated initialize/destroy cycles.
