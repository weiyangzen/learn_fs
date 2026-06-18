
# sources/user-network-fs/rclone/lib/atexit/atexit.go

Purpose: package `atexit` registers cleanup functions to run once on normal shutdown or selected exit signals.

Important APIs/types/functions: globals hold registered function handles, mutexes, signal channel, `sync.Once`s, and atomic `signalled`/`runCalled`. Public APIs are `Register`, `Signalled`, `Unregister`, `IgnoreSignals`, `Run`, and `OnError`. `FnHandle` is a pointer to the registered function value.

Control flow: first `Register` installs a signal goroutine for platform `exitSignals`. On signal, it stops signal delivery, marks signalled, logs, calls `Run`, and exits with platform-specific code. `Run` marks running, locks the function map, and executes registered functions once. `OnError` wraps a cleanup so it runs either at exit or when a deferred error pointer is non-nil.

State/persistence: process-global registry only.

Dependencies/integration: used by `test_all` to force-stop servers and by `batcher` to flush pending batches.

Risks: functions run while holding `fnsMutex`; a handler that tries to register/unregister can deadlock. Map iteration order is nondeterministic. Handlers registered after `Run` starts are ignored.

Test signals: platform exit-code behavior is covered in `atexit_test.go`; signal execution is typically integration-tested by consumers.
