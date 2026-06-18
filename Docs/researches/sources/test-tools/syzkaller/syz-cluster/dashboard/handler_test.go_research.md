# sources/test-tools/syzkaller/syz-cluster/dashboard/handler_test.go

## Purpose
Provides integration-style tests for dashboard URL reachability and patch aggregation behavior.

## Important APIs, types, and functions
`TestURLs` creates an app test environment, starts a controller test server, uploads dummy series with findings, starts the dashboard test server, builds URLs with `api.URLGenerator`, and asserts HTTP 200 responses. `TestAllPatches` uploads a two-patch series and verifies `/series/{id}/all_patches` returns bodies in order. `testServer` constructs `dashboardHandler` and wraps it in `httptest.NewServer`.

## Control flow
The tests populate Spanner/blob state through controller helpers, then exercise the public HTTP handler surface over real HTTP. The URL set includes root, stats, series, session, build logs/configs, and finding logs/repros. Responses are read fully so failures can include response bodies.

## State and persistence behavior
State is isolated in `app.TestEnvironment`; data is persisted through the same repositories and blob storage used in production paths. The test server is closed via `t.Cleanup`.

## Dependencies and integration points
Depends on `pkg/app`, `pkg/controller`, `pkg/api`, and `pkg/db`. It validates integration between dashboard routes, URL generation, controller upload helpers, reporter/finding storage, and blob-backed content retrieval.

## Risks and edge cases
`TestURLs` calls `io.ReadAll(resp.Body)` before checking `err`; if `http.Get` failed, `resp` would be nil. In normal local test conditions the server URL is valid, so this is low risk but brittle. The tests assert successful responses, not rendered HTML details or content types.

## Test signals
Strong signal that core dashboard routes do not panic or return non-200 for representative populated data. `TestAllPatches` specifically guards ordering and concatenation semantics for patch blobs.
