# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.h

Purpose: Declares a reusable GoogleTest fixture for `blockstore::caching::Cache` tests. It standardizes cache construction with minimal key/value types and a fixed capacity so individual tests can work with plain integers.

Important APIs and types: The fixture exposes `push(int,int)`, `pop(int)`, `MAX_ENTRIES = 100`, and a `Cache` alias for `Cache<MinimalKeyType, MinimalValueType, MAX_ENTRIES>`. The private member `_cache` is constructed with name `"test"`.

Control flow: Test cases instantiate the fixture, call helper methods, and inspect optional integer results. The header itself has no runtime logic besides inline construction.

State and persistence behavior: Holds one in-memory cache per test fixture. Static lifetime tracking is delegated to `MinimalKeyType` and `MinimalValueType`.

Dependencies and integration points: Pulls in GoogleTest, production `Cache.h`, minimal type headers, and Boost optional. It is the integration boundary between production templates and readable cache behavior tests.

Risks: The comment still mentions `QueueMap`, so maintainers could confuse the fixture role. The fixed capacity hides capacity-edge behavior unless tests deliberately push over `MAX_ENTRIES`.

Test signals: Any fixture user can validate cache hits, misses, eviction, and type-lifetime behavior without constructing production template arguments manually.
