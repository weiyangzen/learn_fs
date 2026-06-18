# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.cpp

Purpose: Defines static storage for `CopyableMovableValueType::instances`. The corresponding header implements the behavior; this file provides the single translation-unit definition required by the tests.

Important APIs and types: The only API surface is `std::atomic<int> CopyableMovableValueType::instances(0)`, used to track live object counts.

Control flow: There is no runtime control flow beyond static initialization before tests begin.

State and persistence behavior: Maintains process-local atomic live-instance count. No filesystem persistence or external state exists.

Dependencies and integration points: Includes `CopyableMovableValueType.h`; cache and queue tests can link against the static counter when checking value object lifetime.

Risks: Multiple definitions would break linking; missing definition would break tests using the static counter. The counter must be reset by tests when they depend on exact counts.

Test signals: Successful link and accurate instance-count assertions in tests that use the copyable/movable value helper.
