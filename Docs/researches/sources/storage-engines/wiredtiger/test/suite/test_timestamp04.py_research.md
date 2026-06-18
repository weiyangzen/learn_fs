# sources/storage-engines/wiredtiger/test/suite/test_timestamp04.py

## Purpose
`test_timestamp04.py` verifies `rollback_to_stable` visibility rules for timestamped/non-timestamped and logged/non-logged tables under different logging and cache configurations.

## Important APIs, Types, and Functions
The class defines custom connection opening through `ConnectionOpen(cacheSize)`, a `check` helper that can assert missing keys, and `test_rollback_to_stable`. Scenarios vary connection logging mode, cache size, and row/column format.

## Control Flow
The test opens four tables representing timestamp/logging combinations, inserts 10,000 timestamped keys plus non-timestamped values, verifies visibility, sets stable to half the key range, checkpoints, calls `conn.rollback_to_stable`, and checks rollback statistics. It verifies non-timestamped tables keep all data, non-logged timestamped tables retain only stable-range keys, and logged timestamped behavior depends on connection logging. It advances oldest, writes value 2 at later timestamps, advances stable to one quarter into the later range, rolls back again, checks cumulative rollback stats, and verifies expected value 1/value 2 visibility.

## State and Persistence Behavior
The test stresses in-cache and evicted update chains using small pages and optional small cache. Rollback mutates persisted/in-memory state back to stable timestamp while respecting logging rules.

## Dependencies and Integration Points
It integrates with rollback-to-stable, connection statistics, eviction settings, logging, checkpointing, and timestamped reads.

## Risks and Test Signals
Risks include rolling back logged data incorrectly, missing evicted updates, or bad rollback accounting. Signals are exact key dictionaries/missing checks and rollback stat thresholds.
