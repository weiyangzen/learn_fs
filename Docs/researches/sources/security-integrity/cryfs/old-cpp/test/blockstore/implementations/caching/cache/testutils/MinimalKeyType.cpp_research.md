# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.cpp

Purpose: Provides the static live-instance counter definition for `MinimalKeyType`, the restricted key type used by cache and queue map tests.

Important APIs and types: Defines `std::atomic<int> MinimalKeyType::instances(0)`.

Control flow: Only static initialization occurs. Test fixtures reset and inspect this counter around container lifetimes.

State and persistence behavior: Process-local atomic state tracks active key objects. No persisted state exists.

Dependencies and integration points: Includes `MinimalKeyType.h`; links with tests that instantiate `QueueMap<MinimalKeyType,...>` or `Cache<MinimalKeyType,...>`.

Risks: The counter is global to the process, so tests must reset it before exact leak assertions and avoid overlapping lifetimes. Missing or duplicate definitions would break linking.

Test signals: Fixture destructors expect the counter to reach zero after cache/queue destruction, catching leaked key objects or stale internal map entries.
