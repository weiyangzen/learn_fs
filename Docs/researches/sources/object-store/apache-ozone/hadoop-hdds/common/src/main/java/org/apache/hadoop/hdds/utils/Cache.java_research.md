# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/Cache.java

## Purpose
Minimal generic cache abstraction.

## Important APIs and types
Methods are `get`, `put`, `remove`, `removeIf`, and `clear`. `put` can throw `InterruptedException`.

## Control flow and state
No implementation state; behavior is defined by implementers.

## Dependencies and integration points
Shared utility interface for components needing cache implementations with predicate-based removal.

## Risks and test signals
Consumer tests should verify implementation-specific concurrency, interruption, removal, and clear semantics. The interface does not specify null handling or eviction behavior.
