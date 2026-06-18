# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Size.cpp

Purpose: Tests the size accounting contract of `blockstore::caching::QueueMap` through the shared `QueueMapTest` fixture. It verifies an empty map, pushes of one and two values, global oldest pops, keyed pops, and push-after-pop paths including reusing the same key.

Important APIs and types: Uses `QueueMapTest::push`, `pop`, `pop(key)`, and `size`, backed by `QueueMap<MinimalKeyType, MinimalValueType>`. The fixture also validates object lifetime counts after teardown.

Control flow: Each GoogleTest case constructs a fresh fixture, performs a short sequence of queue/map operations, and asserts exact `size()` after each state transition.

State and persistence behavior: State is in-memory only: the queue order, key index, and per-key removals. No filesystem persistence is involved.

Dependencies and integration points: Integrates with `QueueMapTest.h`, minimal non-default-constructible key/value types, `unique_ref`, `boost::optional`, and GoogleTest.

Risks: Off-by-one size drift after removing by key or after reinserting an existing key would break eviction policy in cache users. The tests do not cover multithreading.

Test signals: Exact sizes after every push/pop sequence and fixture teardown with zero leaked keys/values.
