# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.h

Purpose: Declares the shared fixture for `QueueMap` tests. It documents and exposes the minimal test operations needed to validate queue ordering, keyed lookup/removal, peek behavior, size accounting, and leak-free ownership.

Important APIs and types: `QueueMapTest` inherits `::testing::Test` and provides `push(int,int)`, `pop()`, `pop(int)`, `peek()`, and `size()`. It owns a `unique_ref` to `QueueMap<MinimalKeyType, MinimalValueType>`.

Control flow: The header declares operations; implementation in the `.cpp` performs conversions and leak checks.

State and persistence behavior: Fixture state is one in-memory map per test case. Static key/value counters are reset and checked by the implementation.

Dependencies and integration points: Includes GoogleTest, `unique_ref`, production `QueueMap.h`, minimal type headers, and Boost optional.

Risks: The fixture's integer facade is intentionally narrow and will not reveal bugs involving richer key hashing or value copy behavior. It also assumes single-threaded fixture use.

Test signals: Consumers can assert optional return values, size, and peek while the fixture enforces that no internal container nodes leak.
