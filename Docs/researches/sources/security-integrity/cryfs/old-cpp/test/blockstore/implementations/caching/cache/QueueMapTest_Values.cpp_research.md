# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Values.cpp

Purpose: Verifies value-returning behavior and FIFO/keyed removal semantics of `QueueMap`. It covers empty pops, missing keyed pops, pushing one or two values, popping first or last keys, middle/first/last keyed removal from larger queues, many-value FIFO ordering, and replacing an already existing key.

Important APIs and types: Uses `QueueMapTest::push`, `pop`, `pop(key)`, and `peek`, with results represented as `boost::optional<int>`. Includes the Boost optional/gtest workaround so optional values can be asserted cleanly.

Control flow: Tests build deterministic operation traces and compare returned optional values against expected value order. Keyed pops remove a specific key while global `pop` preserves oldest remaining order.

State and persistence behavior: Only in-memory queue/index state is exercised. The fixture's minimal move-only value type catches invalid use-after-move and lifetime leaks.

Dependencies and integration points: Exercises `QueueMap` as used by the caching blockstore layer, where eviction order and key replacement must stay consistent.

Risks: Duplicate-key push behavior is a subtle integration point; stale queue entries can cause wrong value eviction or size mismatches. No concurrent access is tested.

Test signals: Optional none/value checks, FIFO ordering after keyed removal, peek stability, many-value sequence correctness, and zero leaked key/value instances at fixture teardown.
