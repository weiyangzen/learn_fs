# sources/object-store/openstack-swift/swift/proxy/server.py

## Purpose

`server.py` is the Swift proxy WSGI application. It initializes proxy-wide configuration, rings, policy-specific override options, mandatory middleware insertion, request routing, request normalization, backend node sorting/error limiting, and paste.deploy app startup.

## Important APIs and Types

`ProxyOverrideOptions` parses per-policy and default options for node sorting, read/write affinity, write-affinity handoff delete counts, rebalance-missing suppression, concurrent GET behavior, and EC extra requests. `Application` is the WSGI final app and central integration object used by account, container, object, and info controllers.

`Application.__init__` loads timeouts, chunk sizes, cache recheck intervals, skip-cache percentages, account/container/object rings, storage policies, expirer config, CORS and info settings, request node count functions, owner headers, policy overrides, Swift info registration, and the global watchdog. `get_controller` maps `/info`, account, container, and object paths to controller classes; object routing additionally reads container policy and uses `ObjectControllerRouter`.

`handle_request` performs timestamp/token normalization, UTF-8/path/API checks, host-header denial, controller instantiation, transaction id setup, allowed-method checks, authorization preflight/delay-denial handling, and method dispatch. `sort_nodes`, `set_node_timing`, `error_limited`, `error_limit`, `error_occurred`, `check_response`, and `exception_occurred` provide backend node selection and health/error accounting. `modify_wsgi_pipeline` injects mandatory filters such as `catch_errors`, `gatekeeper`, `listing_formats`, `copy`, `dlo`, and `versioned_writes`. `parse_per_policy_config`, `app_factory`, and `main` are startup entry points.

## Control Flow

At startup, `app_factory` merges global/local config, parses `proxy-server:policy:<index>` sections, creates `Application`, and validates configuration. Each WSGI request is wrapped as a `Request`, normalized by `update_request`, validated by `handle_request`, mapped to a controller, authorized if the pipeline installed an auth hook, and dispatched to the controller method. Exceptions are converted to Swift HTTP responses while unhandled errors become HTTP 500.

Backend node ordering starts as a shuffle, then optionally sorts by stored timing or read-affinity. Backend response and exception helpers update the `ErrorLimiter`; object/account/container controllers call these helpers when backend servers timeout, throw, or return 5xx/507 responses.

## State and Persistence

The app stores process-local runtime state: rings, policy override objects, timing cache entries keyed by node IP, error limiter counters, config-derived booleans/limits, a statsd client, and a spawned watchdog. It writes no durable state itself; persistent data lives in backend rings, backend servers, object expirer data, and middleware/config files.

## Dependencies and Integration Points

The file integrates with Swift rings and storage policies, `swift.common.wsgi`, paste.deploy app factories, `swift.common.registry.register_swift_info`, account/container/object/info controllers, object expirer config, statsd metrics, node affinity helpers, mandatory middleware filters, authorization middleware through `swift.authorize`, and backend error-limiter logic.

## Risks and Edge Cases

Per-policy config parsing requires numeric policy indexes; invalid affinity expressions or sorting methods fail startup. `update_request` deliberately removes `Content-Length` when chunked transfer encoding is present to avoid request-smuggling risks. Cached container info with an unknown policy index causes service unavailable until workers reload policy definitions. Node timing is keyed only by IP, so timing data can blur devices/ports sharing an IP. Pipeline mutation depends on filter names and relative ordering; missing or renamed entry points can change middleware behavior. The class-level socket buffer tweak is legacy Python 2 only.

## Test Signals

Tests should exercise policy override parsing and validation, read/write affinity behavior, per-policy concurrent GET settings, request path routing, bad UTF-8/API paths, chunked plus content-length stripping, authorization delay-denial behavior, host-header denial, node sorting modes, error limiter increments and forced limits, mandatory middleware insertion order, app factory config parsing, and unknown storage policy handling.
