# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/slow_operation.py

## Purpose
Provides a reusable polling runner for web API operations that start asynchronously and expose status under `/operations/<handle>`.

## APIs, Types, And Control Flow
`SlowOperationRunner.run(options)` generates a random base32 operation handle, resolves the target alias/path, builds the operation URL via subclass-provided `make_url`, starts it with POST, and then calls `wait_for_results`. Polling uses a fixed schedule of 1, 5, 10, 30, 60, 90, then increasing 120-second intervals. `poll` GETs JSON status with `release-after-complete=true`; if unfinished it continues, if raw output is requested it writes printable ASCII JSON, otherwise it delegates to subclass `write_results`.

## State, Persistence, And Integration
No local persistence. Remote state is the gateway operation handle and server-side operation status, released after completion. Integrates with CLI aliases, `common_http.do_http`, JSON parsing, base32 random handles, and command modules that subclass it for slow operations.

## Risks And Test Signals
Risks include indefinite polling with no client-side timeout, blocking `time.sleep`, operation-handle lifecycle assumptions, and raw JSON output rejecting unprintable bytes. Test signals are slow-operation users such as deep operations/manifest/status tests and web API operation tests.
