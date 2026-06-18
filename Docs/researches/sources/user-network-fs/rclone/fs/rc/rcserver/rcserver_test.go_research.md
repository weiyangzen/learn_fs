# sources/user-network-fs/rclone/fs/rc/rcserver/rcserver_test.go

## Purpose
This large test file validates the HTTP behavior, auth behavior, file/remote serving, RC POST dispatch, async handling, pprof exposure, and security restrictions of the RC server.

## Important APIs, Types, and Functions
- `testRun` describes synthetic HTTP cases.
- `testServer` and `emulateCalls` create a server/router and execute table-driven requests.
- `newTestOpt` builds enabled RC options on `localhost:0`.
- Focused tests include `TestFileServing`, `TestRemoteServing`, `TestCheckServeRemote`, `TestServeRemoteUnauthenticated`, `TestServeRemoteWithAuth`, `TestServeRemoteMarksRCRequest`, `TestRC`, `TestRCWithAuth`, `TestRCAsync`, `TestRCDebug`, `TestServeModTime`, and `TestContentTypeJSON`.

## Control Flow
Tests synthesize requests directly against the chi router or start a real listener for the basic liveness check. Assertions compare exact bodies or regex matches and selected headers. `TestMain` fakes `rclone version` and an unknown command for `core/command` RC tests.

## State and Persistence
Tests install temporary config state, mutate filesystem modtimes in `testdata/files/modtime`, and add cache entries indirectly through local backend use. They rely on static test fixtures under `testdata`.

## Dependencies and Integration Points
The test imports the local backend, `configfile`, `fs`, RC registry, `httptest`, and the server's router. It verifies integration with `core/command`, jobs, pprof, static serving, remote listing, and auth middleware.

## Risks and Edge Cases
The exact response-body assertions are valuable but can be brittle across template or JSON formatting changes. The security tests are especially important because remote serving can instantiate backends from URL-derived strings.

## Test Signals
Coverage is strong for HTTP status/body/header behavior, content-type parsing, JSON charset validation, form parsing failures, async `Prefer` behavior, auth enforcement, no-auth overrides, and the RC-request marker that prevents `global.*` config mutation.
