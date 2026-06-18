# sources/object-store/openstack-swift/swift/common/middleware/memcache.py

Purpose: Minimal WSGI middleware that loads Swift's configured memcache client once and injects it into each request environment as `swift.cache`.

Important APIs and control flow: `MemcacheMiddleware.__init__` records the downstream app, creates a route-specific logger, and calls `load_memcache(conf, logger)`. `__call__` assigns the resulting client to `env['swift.cache']` before delegating. `filter_factory` merges global and local PasteDeploy config and returns the filter wrapper.

State, dependencies, and integration: The only long-lived state is the loaded memcache client object. It is consumed by other middleware such as ratelimit, auth, account/container info caches, and request helper code via `cache_from_env` or direct `swift.cache` access.

Risks and test signals: Because every request gets the same client reference, tests should verify initialization happens once and request environ injection happens every time. Misconfiguration or unavailable memcache is mostly handled inside `load_memcache`; integration tests should cover downstream middleware behavior when `swift.cache` is absent versus present.
