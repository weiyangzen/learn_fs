# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h

Purpose: Defines the per-entry wrapper for the caching layer, storing a cached value and the time it was inserted/accessed for age-based purging.

Important APIs and types: `CacheEntry<Key, Value>` has a constructor, move constructor, `ageSeconds`, and `releaseValue`. It stores a Boost `ptime` `_lastAccess` and a `Value`.

Control flow: Construction records `currentTime()` and moves in the value. `ageSeconds` subtracts `_lastAccess` from the current local time and converts nanoseconds to seconds. `releaseValue` moves the value out.

State and persistence behavior: State is in memory only. The timestamp controls when `Cache` considers an entry old; there is no refresh on pop/push beyond construction time.

Dependencies and integration points: Depends on Boost posix time, cpp-utils macros, and cache eviction logic in `Cache.h`.

Risks: Uses local wall-clock time instead of a monotonic clock, so system clock changes can affect age. The comment in `Cache.h` notes lifetime is based on last push, not true repeated access lifetime. Moving out leaves the internal value moved-from until the entry is erased.

Test signals: Indirect cache tests should validate age purging and value release. There are no local tests.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/CacheEntry.h` completely for this pass (44 lines, 1050 bytes).
