# sources/test-tools/syzkaller/syz-cluster/dashboard/main.go

## Purpose
Entry point for the dashboard binary.

## Important APIs, types, and functions
`main` creates a background context, loads an application environment with `app.Environment(ctx)`, constructs `newHandler`, creates an `http.Server` at address `:8081`, and serves the handler mux. Fatal initialization and serve errors go through `app.Fatalf`.

## Control flow
Startup is linear: environment, handler, server, listen. There is no graceful shutdown hook in this file; process termination is expected to be managed by the runtime environment.

## State and persistence behavior
No direct persistence. Runtime state is acquired from the app environment, including config, Spanner, and blob storage.

## Dependencies and integration points
Integrates with Kubernetes deployment/service expecting container port 8081 and `web-dashboard-service` mapping to port 80. Depends on the same handler/template/static files researched above.

## Risks and edge cases
Server uses `ListenAndServe` without explicit read/write timeouts. Any environment initialization failure terminates the process. The bind address is hard-coded.

## Test signals
Exercised indirectly by local cluster smoke deployment and handler tests; the `main` function itself has no direct unit test.
