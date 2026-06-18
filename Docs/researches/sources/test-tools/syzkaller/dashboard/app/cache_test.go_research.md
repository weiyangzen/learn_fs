# sources/test-tools/syzkaller/dashboard/app/cache_test.go

Purpose: tests the user-interface cache paths implemented in `cache.go`.

Important tests: `TestCachedBugGroups` creates bugs at different reporting/access stages, adds a separate namespace to guard against cross-namespace contamination, records the uncached output from `fetchNamespaceBugs`, runs `/cron/minute_cache_update`, reads `CachedBugGroups`, and asserts cached groups exactly match original groups for public and user access. It also confirms the namespace page can render after the cache is populated. `TestBugListWithoutCache` verifies pages for public, user, and admin access levels render when `CacheUIPages` is enabled but memcache has no entry.

Control flow under test: build upload, crash report, reporting poll/update, cross-namespace data creation, direct uncached fetch, authenticated cron GET, memcache retrieval, and page GET.

State and persistence behavior: tests drive datastore state for bugs/builds/reporting and memcache state for compressed bug groups. The empty-cache test asserts normal request paths fall back to datastore rather than requiring warm minute cache.

Dependencies and integration points: uses `dashapi`, `testConfig` access-public namespace behavior, `Ctx` helpers, `fetchNamespaceBugs`, `CachedBugGroups`, `/cron/minute_cache_update`, and page handlers.

Risks covered: access-level leakage, namespace mixing, stale or malformed compressed cache objects causing page failures, and accidental dependency on cache warmup. It does not cover hourly aggregate `CacheGet`, manager list caches, or throttle CAS behavior.
