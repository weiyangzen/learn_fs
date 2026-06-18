# sources/object-store/openstack-swift/swift/common/middleware/ratelimit.py

Purpose: Enforces account, container, listing, and account-wide write rate limits using memcache as a distributed leaky-bucket clock.

Important APIs and control flow: `interpret_conf_limits` parses size-threshold config into interpolation functions; `get_maxrate` chooses the applicable rate by container size. `RateLimitMiddleware` loads account, container, listing, whitelist, blacklist, clock, buffer, and sleep settings. `get_ratelimitable_key_tuples` derives memcache keys for account container PUT/DELETE, object writes, container listings, and account sysmeta `global-write-ratelimit`. `_get_sleep_time` increments a memcache timestamp key, calculates required sleep, resets stale buckets, decrements on max-sleep rejection, and ignores memcache connection failures. `handle_ratelimit` fetches account info, honors whitelist/blacklist sysmeta, sleeps when needed, and returns custom 497/498 responses on hard denials.

State, dependencies, and integration: Persistent coordination is in memcache keys. Request state includes `swift.ratelimit.handled` to avoid duplicate handling. It depends on `cache_from_env`, account/container info helpers, and Swift info registration.

Risks and test signals: Missing memcache disables protection. Clock accuracy, max sleep, and stale bucket resets are subtle. Tests should cover interpolation, black/white lists, sysmeta overrides, duplicate handling, memcache errors, max-sleep rollback, global write limits, and pipeline behavior without valid Swift paths.
