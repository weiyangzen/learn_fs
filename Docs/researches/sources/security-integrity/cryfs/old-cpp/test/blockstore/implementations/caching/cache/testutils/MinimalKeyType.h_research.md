# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.h

Purpose: Defines a deliberately minimal key type for testing cache templates. It is non-default-constructible, copyable, hashable, equality-comparable, and live-counted, forcing production containers to rely only on required key operations.

Important APIs and types: `MinimalKeyType::create(int)`, copy constructor, destructor, `value()`, static `instances`, `std::hash<MinimalKeyType>`, and `operator==`.

Control flow: Keys are constructed only through the private integer constructor via `create`. Copy construction delegates to value construction, incrementing the instance count; destruction decrements it.

State and persistence behavior: Each key owns one integer. Global atomic instance count is process-local test state and is used for leak detection.

Dependencies and integration points: Integrates with `std::unordered_map` through a hash specialization and equality operator. This matches `QueueMap`/`Cache` lookup needs without default construction.

Risks: The hash is simply the integer value, adequate for deterministic tests but not collision-heavy scenarios. Static count assertions require clean fixture isolation.

Test signals: Successful compilation with non-default-constructible keys, correct keyed lookup/removal, and zero remaining instances after tested containers are destroyed.
