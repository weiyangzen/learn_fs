# sources/object-store/openstack-swift/swift/common/middleware/backend_ratelimit.py

Purpose: backend WSGI middleware that rate-limits storage-node requests per device and per `(device, method)` to protect backend disks from request bursts.

Important APIs/types/functions: constants define rate-limited methods, config section/file names, reload interval, default rates, and rate buffer. `BackendRateLimitMiddleware` owns config state, rate limiter maps, config reloads, limiter creation, allow checks, and WSGI request handling. `filter_factory` merges paste config and returns the filter.

Control flow: initialization reads startup filter config, identifies the optional external `backend-ratelimit.conf`, applies defaults and method-specific rates, and attempts to load file overrides. `_apply_config` builds a `{None: aggregate, METHOD: per-method}` rate map and refreshes existing limiter rates when changed. `_maybe_reload_config` periodically reloads config and always advances the attempt timestamp to avoid retry storms. On each request, `__call__` reloads if due, wraps the env as a `Request`, and if any limit is configured and the method is limited, validates the backend path as device/partition. Requests without valid backend device paths pass through. Valid backend requests must pass both aggregate device and per-method limiters; failures increment `backend.ratelimit` and return `HTTPTooManyBackendRequests` (529).

State and persistence: in-memory config, limiter token state, last reload time, and expected-file flag. Optional persistent config lives in `backend-ratelimit.conf`.

Dependencies and integration: depends on Swift request path validation, `swob` request/HTTP exceptions, logging, `non_negative_float`, `EventletRateLimiter`, and `readconf`. It runs in backend server pipelines for account, container, and object services.

Risks: limiter keys retain entries for removed devices; aggregate and method limits both consume limiter state, so checks must remain ordered intentionally; invalid config leaves prior config active; reload interval zero disables reload; all methods not listed bypass rate limiting. Tests should cover default disabled behavior, external config load/reload/failure, aggregate and method-specific throttling, path parse pass-through, limiter refresh on config change, invalid numeric config, and 529 metric increments.
