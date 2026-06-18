# Research: sources/sync-backup/syncthing/test/http_test.go

## sources/sync-backup/syncthing/test/http_test.go

Purpose: integration tests and benchmarks for GUI/static serving, authentication, CSRF protection, and REST API performance.

Important APIs/functions: `TestHTTPGetIndex`, `TestHTTPGetIndexAuth`, `TestHTTPOptions`, `TestHTTPPOSTWithoutCSRF`, `setupAPIBench`, `benchmarkURL`, and six `BenchmarkAPI_*` functions.

Control flow: starts h1 or h2, uses raw `net/http` requests for page/auth/CSRF checks, extracts CSRF cookie and device short ID header, then tests POST success/failure. Benchmarks create a large dataset and repeatedly call REST endpoints through `rc.Process.Get`.

State and persistence: mutates `s1`, `s2`, and indexes during benchmark setup; reads GUI responses over local HTTP ports.

Dependencies and integration: `lib/protocol`, `lib/rc`, HTTP server, GUI asset serving, API key/basic auth/CSRF middleware. Risks include cookie parsing by string slicing, fixed ports, and benchmark setup cost. Test signals are status codes, response content, cookies, and benchmark throughput.
