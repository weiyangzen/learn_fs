# sources/test-tools/syzkaller/dashboard/app/cache.go

Purpose: maintains App Engine memcache-backed summaries for dashboard pages and implements request throttling keyed by requester identity.

Important APIs and types: `Cached` stores aggregate bug stats, subsystem stats, no-subsystem stats, and missing-backport count. `CacheGet` loads a per-namespace/per-access summary from memcache or rebuilds it from bugs and backports. `cacheUpdate` refreshes summaries hourly for every namespace and public/user/admin access levels. `CachedBugGroups`, `handleMinuteCacheUpdate`, and `minuteCacheNsUpdate` cache compressed JSON UI bug groups for namespaces with `CacheUIPages`. `CachedManagerList`, `CachedUIManagers`, and generic `cachedObjectList` memoize manager-derived lists. `RequesterInfo.Record` and `ThrottleRequest` enforce sliding-window throttling using memcache CAS.

Control flow: page code calls `CacheGet` or UI cache getters; cron refreshes slow caches out-of-band. Minute cache refresh loads visible bugs and managers, prepares bug groups for each access level, marshals/compresses them, and stores them for two minutes. Throttling reads or creates a requester record, prunes old timestamps, appends the current time, stores at most `Limit+1` timestamps, and retries CAS conflicts up to five times.

State and persistence behavior: all state is in memcache with short expirations; cache misses rebuild from datastore. Cached UI bug groups are JSON compressed via `pkg/image`; other cached lists use memcache Gob. Throttle records expire after the configured window and are hashed by requester ID to avoid raw identifiers in keys.

Dependencies and integration points: uses `loadNamespaceBugs`, `loadAllBackports`, `loadVisibleBugs`, `prepareBugGroups`, `managerList`, `loadManagers`, `bug.sanitizeAccess`, `ThrottleConfig`, `timeNow`, App Engine memcache/logging, and dashboard request access-level helpers.

Risks: cache data is access-level sensitive, so key construction and sanitize checks are critical. `RequesterInfo.Record` sorts `ri.Requests` rather than `newRequests`, a likely harmless but suspicious line because `newRequests` is assigned afterward. Memcache failures bubble up to requests for some paths. CAS conflict logic intentionally avoids retrying denied requests in some cases, which favors throttling under contention.

Test signals: `cache_test.go` verifies cached bug groups match uncached fetches for public/user views and that namespace pages still render with empty cache.
