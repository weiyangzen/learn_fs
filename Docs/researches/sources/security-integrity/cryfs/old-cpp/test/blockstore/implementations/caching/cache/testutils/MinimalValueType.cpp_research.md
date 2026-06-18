# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.cpp

Purpose: Supplies the static live-instance counter definition for `MinimalValueType`, the move-only value used by queue/cache tests.

Important APIs and types: Defines `std::atomic<int> MinimalValueType::instances(0)`.

Control flow: No functions are implemented here; only static initialization is performed before test execution.

State and persistence behavior: The process-local atomic count tracks active minimal values and is checked by fixtures after container destruction.

Dependencies and integration points: Includes `MinimalValueType.h`; required at link time for all tests using the move-only value helper.

Risks: Because the counter is static, unrelated tests sharing the type can contaminate exact counts if they overlap or fail before cleanup.

Test signals: Link success and fixture leak checks reaching zero are the primary signals.
