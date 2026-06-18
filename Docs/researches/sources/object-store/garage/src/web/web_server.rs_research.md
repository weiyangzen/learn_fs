<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/web_server.rs -->
# sources/object-store/garage/src/web/web_server.rs

## Purpose
Implements Garage's S3 static website endpoint: listener setup, request logging/metrics/tracing, bucket resolution from host, website routing rules, object GET/HEAD serving, redirects, error documents, and CORS.

## Important APIs, types, and functions
Important types are `WebMetrics`, `WebServer`, and private `RoutingResult`. Key functions are `WebServer::new`, `run`, `handle_request`, `check_key_exists`, `serve_file`, `handle_inner`, `error_to_res`, `RoutingResult::main_target`, `path_to_keys`, and `compute_redirect_target`.

## Control flow
`run` binds TCP or Unix sockets and delegates to the common server loop. Each request logs peer or forwarded IP, starts an OpenTelemetry span, records metrics, maps the body away, and calls `serve_file`. `serve_file` requires Host, maps host/root domain to bucket alias, loads bucket website config, applies path/routing rules, then either redirects or calls S3 GET/HEAD handlers. It also handles website redirect metadata, error documents, and CORS headers.

## State and persistence behavior
The server reads bucket alias, bucket configuration, and object tables through the `Garage` model. It does not write persistent state. Metrics counters/recorders track request and error counts/durations in memory/exported telemetry.

## Dependencies and integration points
Deeply integrates Hyper, Tokio listeners, Garage common server loop, S3 object handlers, bucket table routing rules, CORS helpers, forwarded header parsing, table lookups, and OpenTelemetry.

## Risks and test signals
Routing is subtle: percent-decoding, trailing-slash redirects, alternative error keys, and HTTP redirect code handling must match S3 website expectations. Host-derived bucket selection depends on trusted root-domain configuration. Existing tests cover `path_to_keys`; broader tests should cover routing rules, error document fallback, HEAD/OPTIONS behavior, CORS, Unix socket binding, and website redirect object metadata.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/web_server.rs -->
