# sources/user-network-fs/rclone/lib/cache/cache.go

## Purpose
`cache.go` implements a small thread-safe string-keyed cache for arbitrary values. Entries expire after a period of disuse, can store creation errors for negative caching, can be pinned against expiry, and can run a finalizer when removed.

## Important APIs, types, and functions
- `Cache` holds the protected map, expiry settings, timer state, and finalizer.
- `cacheEntry` stores value, cached error, key, `lastUsed`, and `pinCount`.
- `CreateFunc` creates values and reports whether an error should still be cached.
- Public operations include `New`, `SetExpireDuration`, `SetExpireInterval`, `Get`, `PutErr`, `Put`, `GetMaybe`, `Delete`, `DeletePrefix`, `Rename`, `Clear`, `Entries`, `SetFinalizer`, `Pin`, `Unpin`, and `EntriesWithPinCount`.
- `cacheExpire` is the timer callback that removes old unpinned entries.

## Control flow
`Get` locks the cache, returns an existing entry when present, or unlocks while running the caller's `CreateFunc` so recursive cache use cannot deadlock. If creation returns an error with `ok == false`, the error is returned but not cached. Otherwise the new entry is inserted unless caching is disabled, then `used` updates `lastUsed` and starts an expiry timer if needed. Removal functions call `finalize` before deletion. `Rename` prefers an existing `newKey` entry, finalizes the displaced old value if distinct, and otherwise moves `oldKey` to `newKey`.

## State and persistence behavior
All state is in memory. Expiry uses `time.AfterFunc`; the boolean `expireRunning` ensures only one scheduled expiry chain exists while the cache has live entries. `SetExpireDuration(<=0)` disables caching, while `SetExpireInterval(<=0)` effectively disables periodic expiry by setting a very long interval.

## Dependencies and integration points
The package depends only on the Go standard library. It is a generic utility used by higher-level rclone components that need short-lived process-local memoization, including caches that need finalizers for resource cleanup.

## Risks and edge cases
`Get` has a duplicate-creation race: two goroutines missing the same key can both run `create`, and the later insert wins. That is acceptable for simple memoization but unsafe for create functions with non-idempotent side effects. `Pin`/`Unpin` can drive `pinCount` negative; expiry treats non-positive as unpinned. Finalizers run while the cache mutex is held, so slow or reentrant finalizers can block the cache or deadlock. Timer callbacks are not cancellable after `Clear`; they will run later and observe the empty map.

## Test signals
`cache_test.go` covers ordinary get reuse, cached errors, uncached errors, explicit put, disabled caching, expiry timing, pinning, clearing, entry counts, maybe-get, deletion, prefix deletion, rename collision behavior, and finalizer calls.
