# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.cpp

Purpose: Implements the tiny `CacheTest` fixture adapter for cache tests using minimal key/value types. It wraps the production cache API in integer-oriented helpers to keep tests focused on behavior rather than construction details.

Important APIs and types: Defines `CacheTest::push(int,int)` and `CacheTest::pop(int)`. The wrapped cache type is `blockstore::caching::Cache<MinimalKeyType, MinimalValueType, MAX_ENTRIES>`.

Control flow: `push` converts integers into `MinimalKeyType` and `MinimalValueType` factory-created objects, then calls `_cache.push`. `pop` builds a key, calls `_cache.pop`, returns `boost::none` on misses, and converts hits back to the stored integer value.

State and persistence behavior: State is entirely in the fixture's in-memory cache. No persistent store, files, or static fixture state are updated here.

Dependencies and integration points: Includes `CacheTest.h`, which brings in GoogleTest, the cache implementation, and minimal type definitions.

Risks: Because this adapter strips values to integers, it is good for cache semantics but not for testing richer value object behavior. Ownership/lifetime checking depends on the minimal types used by the header.

Test signals: Downstream cache tests use this file's helpers to assert optional hit/miss values without exposing production template complexity.
