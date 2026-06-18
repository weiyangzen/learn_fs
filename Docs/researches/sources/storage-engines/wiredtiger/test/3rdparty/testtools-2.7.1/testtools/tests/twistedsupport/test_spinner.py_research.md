<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py

## Purpose

This module tests the low-level Twisted reactor spinner in `testtools.twistedsupport._spinner`. The spinner runs callables inside the reactor, waits for deferred completion, prevents re-entry, traps unhandled deferred errors, handles timeouts/SIGINT, and detects leftover reactor state.

## Important APIs, Types, And Functions

- `_spinner` is imported with `try_import`; Twisted `defer` and `Failure` are optional imports.
- `TestNotReentrant` verifies the `not_reentrant` decorator raises `_spinner.ReentryError` on direct and mutual recursion.
- `TestTrapUnhandledErrors` verifies `trap_unhandled_errors` returns normal function results and captures unhandled deferred failures.
- `TestRunInReactor` exercises `Spinner.run`, `_clean`, `get_junk`, and `clear_junk`.
- `make_reactor`, `make_spinner`, and `make_timeout` centralize access to the real reactor and short timeouts.
- `test_suite()` exposes standard loader integration.

## Control Flow

`Spinner.run(timeout, function, *args, **kwargs)` is tested for direct return values, exceptions, keyword forwarding, deferred success, reentry errors, timeout errors, signal behavior, and cleanup behavior. Reactor cleanup tests create delayed calls, canceled calls, TCP listening ports, and reactor threadpool work, then assert whether `_clean` cancels/removes or records leftover junk. Signal tests schedule `os.kill(os.getpid(), SIGINT)` while the reactor is running and expect `_spinner.NoResultError`.

## State And Persistence Behavior

No durable state is written. Runtime state includes Twisted reactor delayed calls, listening ports/selectables, threadpool threads, signal handlers, a spinner's internal junk list, and local call logs. Tests restore signal handlers with cleanups and require spinner cleanup to leave thread enumeration unchanged after running reactor thread work.

## Dependencies

Depends on `os`, `signal`, `testtools.skipIf`, `try_import`, matchers `Equals`, `Is`, `MatchesException`, and `Raises`, `NeedsTwistedTestCase`, and optional Twisted reactor/defer/failure/protocol modules.

## Integration Points

The spinner is a support primitive for `AsynchronousDeferredRunTest`. Its behavior determines whether Twisted tests can run inside normal testtools runs without leaking reactor state or hanging indefinitely.

## Risks And Edge Cases

Risks include nested reactor spins, unhandled deferred errors being lost, signal handlers being overwritten, timed-out deferreds affecting later runs, stale junk being ignored, listening ports remaining registered, delayed calls not being canceled, and threadpool work leaking threads. POSIX-only SIGINT tests protect interrupt handling.

## Test Signals

Signals are raised `_spinner` exception types, exact return object identity, call logs, restored signal handlers, `_clean` results, `get_junk` contents, canceled delayed-call state, unchanged thread enumeration, and successful second spinner run after a previously timed-out deferred later fires.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_spinner.py -->
