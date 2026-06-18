# sources/storage-engines/tikv/src/server/status_server/lite.rs

## Purpose

`lite.rs` implements a stripped-down TiKV status server intended for short-lived or batch `tikv-ctl` tasks that need observability without a fully bootstrapped TiKV server. It exports metrics, CPU profiling, heap profiling, and async task tracing while intentionally omitting operational endpoints such as config reloads and region metadata dumps.

## Important APIs, Types, And Functions

- `type Svc = StatusServer<()>` aliases the full generic status server with an empty router so this file can call existing static handler methods.
- `Server` owns an `Arc<SecurityConfig>` and is the builder/launcher for the lite HTTP server.
- `Handle` stores the bound `SocketAddr`; `Handle::address()` exposes it to callers and tests.
- `Server::new(sec)` constructs the lite server from shared security configuration.
- `Server::start(status_addr)` parses and binds the requested address, selects TLS or plain Hyper accepting based on whether cert/key/CA paths are all configured, spawns the serving future, and returns the local address.
- `Server::start_serve()` is generic over Hyper acceptors and TiKV's `ServerConnection`, builds per-connection services, captures optional client certificates, and runs `LiteService`.
- `LiteService` is a copyable request dispatcher with `call(RequestCtx)`.
- `RequestCtx` bundles the Hyper request, optional peer `X509` certificate, and shared security config.

## Control Flow

Callers construct `Server::new(Arc<SecurityConfig>)` and call `start()`. `start()` parses `status_addr` into `SocketAddr`, binds `AddrIncoming`, stores `incoming.local_addr()` in the returned handle, and chooses between `tls_incoming(self.security_config.clone(), incoming)` and the raw incoming socket. It then delegates to `start_serve()` and returns immediately after spawning the Hyper server on the current Tokio runtime.

`start_serve()` creates a mutable `LiteService` and passes a service factory to Hyper. For each accepted connection it extracts `conn.get_x509()`, clones the security config, and returns a `service_fn` that clones those per request. Each request is wrapped into `RequestCtx` and passed to `svc.call()`. Server-level Hyper errors are logged with `warn!`.

`LiteService::call()` copies the request path and method, decides whether certificate authorization is required, optionally rejects the request with `403 FORBIDDEN`, and dispatches the accepted subset:

- `GET /metrics` -> `StatusServer::metrics_to_resp(req, true)`.
- `GET /debug/pprof/profile` -> `StatusServer::dump_cpu_prof_to_resp(req).await`.
- `GET /async_tasks` -> `StatusServer::dump_async_trace()`.
- `GET /debug/pprof/heap` -> `StatusServer::dump_heap_prof_to_resp(req)`.
- Anything else -> `404 NOT_FOUND`.

The certificate bypass list is intentionally smaller than the full status server: only `GET /metrics` and `GET /debug/pprof/profile` are unauthenticated when TLS security is configured.

## State And Persistence Behavior

The lite server does not own TiKV data state. It persists only the bound socket listener inside the spawned Hyper server and returns the address through `Handle`. The server task is detached with `tokio::spawn`; there is no explicit stop handle in this file. Request state is per-call and cloned from connection/request context. Profiling handlers can allocate buffers, spawn profiling work, or read heap profile files through the shared `StatusServer` static methods, but this module itself does not persist those artifacts.

## Dependencies

This module depends on Hyper for HTTP serving, Tokio for async runtime and spawning, OpenSSL `X509` for client certificates, `security::SecurityConfig` for TLS/authz configuration, and status-server helpers from the parent module: `StatusServer`, `make_response`, `tls_incoming`, `check_cert`, `make_service_fn`, and the `ServerConnection` trait. It also relies on full status-server profiling/metrics implementations and the Prometheus registry through `metrics_to_resp`.

## Integration Points

- Reuses full status-server handler methods instead of duplicating metrics/profiling logic.
- Shares TLS/client-certificate plumbing with the full status server through `tls_incoming`, `ServerConnection::get_x509`, and `check_cert`.
- Intended for `tikv-ctl` or similar short-term tasks where the full `StatusServer<R>` dependencies, router, config controller, and resource managers are unavailable.
- `GET /debug/pprof/heap` can transitively use `profile.rs` and `jeprof.in` when the request selects the jeprof heap SVG path.

## Risks And Edge Cases

- `Server::start()` panics if called outside a Tokio runtime because `start_serve()` uses `tokio::spawn`.
- The returned `Handle` has no shutdown channel, so lifecycle control is limited once spawned.
- TLS is enabled only when cert, key, and CA paths are all non-empty. Partial security configuration silently falls back to plaintext serving.
- `LiteService` bypasses certificate checks for CPU profile and metrics, matching the local policy in this file. CPU profiling can be expensive, so exposure should be considered when binding non-loopback addresses.
- Unlike the full status server, this lite dispatcher does not record `STATUS_REQUEST_DURATION`, so request latency metrics may be absent for lite-only status traffic.
- `let mut svc = LiteService` is captured by the service factory. `LiteService` is zero-sized and `Copy`, so this is safe, but future stateful additions to `LiteService` would need care around sharing and mutation.

## Test Signals

- `test_server_start_insecure` verifies binding on `127.0.0.1:0` and that the returned address is IPv4.
- `test_lite_service_call_metrics` registers a test Prometheus counter, calls `GET /metrics`, and asserts a successful response containing the series.
- `test_lite_service_call_profile` calls `GET /debug/pprof/profile?seconds=1` without a certificate and expects `200 OK` plus SVG content type.
- `test_lite_service_call_not_found` verifies unknown paths return `404 NOT_FOUND`.
- Missing direct tests include TLS startup, certificate-required routes such as heap and async task tracing, and lifecycle/shutdown behavior.
