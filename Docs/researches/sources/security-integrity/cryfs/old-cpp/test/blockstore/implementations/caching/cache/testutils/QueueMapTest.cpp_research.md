# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.cpp

Purpose: Implements the reusable `QueueMapTest` fixture for behavior tests against `blockstore::caching::QueueMap` using minimal key and move-only value types.

Important APIs and types: Implements constructor, destructor, `push`, global `pop`, keyed `pop`, `peek`, and `size`. The fixture owns `unique_ref<QueueMap<MinimalKeyType, MinimalValueType>>`.

Control flow: Construction creates a fresh `QueueMap` and resets live-instance counters. Destruction explicitly destroys the map and then asserts no key/value instances remain. Helpers translate integer inputs into minimal objects and optional production values back into optional integers.

State and persistence behavior: All state is in-memory. Explicit destruction before leak assertions ensures internal queue/map nodes are released before counters are read.

Dependencies and integration points: Uses `cpputils::make_unique_ref`, `cpputils::destruct`, Boost optional, and the production queue map template.

Risks: The fixture hides full key/value objects, so tests focus on semantics and lifetime but not object identity. Counter resets assume one fixture at a time.

Test signals: Wrapper users get deterministic integer behavior plus automatic leak detection on every test case.
