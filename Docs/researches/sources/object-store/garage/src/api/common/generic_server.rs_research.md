## sources/object-store/garage/src/api/common/generic_server.rs

Purpose: generic HTTP/1 API server framework shared by S3, K2V, and admin-like API handlers.

Important APIs/types/functions: traits `ApiEndpoint`, `ApiError`, `ApiHandler`, struct `ApiServer<A>`, `run_server`, request `handler`, `handler_stage2`, `Accept`, `UnixListenerOn`, and `server_loop`.

Control flow: `ApiServer::new` registers OpenTelemetry metrics. `run_server` binds TCP or Unix sockets, sets Unix permissions, and enters `server_loop`. Each connection is served by hyper HTTP/1. `handler` logs source/key/method/URI, creates a trace span, calls `handler_stage2`, converts API errors to HTTP responses, and logs server errors at warn level. `handler_stage2` parses endpoint, annotates span, measures handler duration, increments counters, and counts error responses.

State/persistence: no domain state, but holds metrics instruments and API handler state. Unix socket path may be removed/recreated and permissions set.

Dependencies/integration: uses hyper/http-body-util/hyper-util, tokio listeners, OpenTelemetry, forwarded-header parsing, and Garage error/metrics utilities.

Risks: only HTTP/1 is served. Error body construction trusts `ApiError`. Shutdown allows 10 seconds for active connections then aborts remaining tasks. Forwarded header parsing affects access logs. Admin `/health` and `/metrics` are logged at debug to reduce noise.

Test signals: no local tests. Integration should verify graceful shutdown, Unix socket permissions, metrics, and error response mapping.
