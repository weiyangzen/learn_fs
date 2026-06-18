# sources/distributed-fs/tahoe-lafs/src/allmydata/util/cputhreadpool.py

## Purpose

This module owns a global Twisted thread pool for CPU-intensive work so Tahoe does not consume the reactor's general thread pool used by DNS and other blocking operations. The pool starts at import time and is sized from `os.cpu_count()`.

## APIs and control flow

`defer_to_thread()` is an async wrapper around `deferToThreadPool()` that runs a callable in `_CPU_THREAD_POOL` and awaits its result. If `_DISABLED` is true, it calls the function synchronously. `disable_thread_pool_for_test(test)` flips `_DISABLED` and registers a cleanup on a `unittest.TestCase`. Import-time setup starts the pool and either registers `_CPU_THREAD_POOL.stop` with `threading._register_atexit` or makes worker threads daemon-capable on older Python.

## State, dependencies, risks, and tests

State is the global `_CPU_THREAD_POOL` and `_DISABLED` flag. Dependencies include Twisted threadpool APIs, the global reactor, Python threading internals, typing helpers, and unittest cleanup. Integration is with CPU-bound code paths that must not block the reactor.

Risks include import-time side effects, reliance on private `threading._register_atexit`, too many threads under cgroups/affinity constraints, and synchronous test mode masking race behavior. Test signals should verify threaded execution, exception propagation, synchronous disable/restore, shutdown behavior, and no accidental use of the default reactor pool.
