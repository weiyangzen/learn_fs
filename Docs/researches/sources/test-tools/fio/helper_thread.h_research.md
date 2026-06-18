# sources/test-tools/fio/helper_thread.h

## Purpose
Declares the helper-thread lifecycle and action API used by fio runtime code.

## Important APIs, Types, and Functions
Forward-declares `struct fio_sem` and `struct sk_out`. Exposes `helper_thread_create`, `helper_thread_exit`, `helper_thread_destroy`, `helper_reset`, `helper_do_stat`, and `helper_should_exit`.

## Control Flow
Callers create the helper with a startup semaphore and socket output context, use reset/stat functions while jobs run, ask whether exit is requested, then call exit and destroy during shutdown.

## State and Persistence Behavior
The header exposes no state. The implementation owns the single global helper instance and its action pipe.

## Dependencies and Integration Points
Included by fio runtime setup, signal/status paths, and shutdown code that need to coordinate periodic background maintenance.

## Risks
The API is singleton-oriented; creating multiple helpers is not supported. `helper_do_stat()` has signal-handler constraints that callers must preserve.

## Test Signals
Compile-time API coverage plus integration tests that start fio jobs with status intervals and verify clean helper startup/shutdown are the primary signals.
