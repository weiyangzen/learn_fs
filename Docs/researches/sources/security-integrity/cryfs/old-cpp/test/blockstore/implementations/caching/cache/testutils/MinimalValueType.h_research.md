# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.h

Purpose: Defines a restrictive move-only value type for cache and queue map tests. It is non-default-constructible and non-copyable, so production templates must support move-only payloads and avoid invalid moved-from access.

Important APIs and types: `MinimalValueType::create(int)`, move constructor, move assignment, destructor, `value()`, static `instances`, and `DISALLOW_COPY_AND_ASSIGN`.

Control flow: Construction increments the count; moving copies the integer payload into a new valid object and marks the source moved; `value()` asserts the object is neither moved nor destructed; destruction asserts it has not already been destroyed and decrements the count.

State and persistence behavior: Per-object state is integer payload plus moved/destructed flags. Global atomic count is process-local test state.

Dependencies and integration points: Uses CryFS assertion/macros and is consumed by `QueueMapTest` and `CacheTest` fixtures.

Risks: The type is intentionally unforgiving; accidental access to moved-from values aborts or throws depending on assertion mode. Tests must account for move semantics rather than copy semantics.

Test signals: Move-only compilation, correct integer values returned from containers, assertion-free movement, and zero live instances at teardown.
