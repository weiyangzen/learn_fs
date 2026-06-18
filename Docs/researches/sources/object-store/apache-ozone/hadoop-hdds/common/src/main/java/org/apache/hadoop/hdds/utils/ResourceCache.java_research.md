# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/ResourceCache.java

## Purpose
Implements Ozone's `Cache<K,V>` using Guava weighted cache eviction to bound cached resource usage.

## Important APIs, Types, And Functions
The constructor requires a Guava `Weigher<K,V>`, a maximum weight, and an optional `RemovalListener<K,V>`. The `Cache` methods are `get`, `put`, `remove`, `removeIf`, and `clear`.

## Control Flow
Construction builds a `CacheBuilder.maximumWeight(limits).weigher(weigher)` cache, adding the listener when supplied. `get()` delegates to `getIfPresent`, `put()` to `put`, `remove()` to `invalidate`, `removeIf()` scans `cache.asMap().keySet()` and invalidates matching keys, and `clear()` invalidates all entries.

## State And Persistence
All mutable state is Guava cache state in memory. There is no ordering metadata in this class beyond Guava's eviction implementation, and no persistent storage.

## Dependencies And Integration Points
Depends on Guava cache APIs and Ozone's local `Cache` interface. Removal listeners integrate with resource cleanup such as closing buffers or file handles.

## Risks
The class comment says FIFO, but Guava maximum-weight eviction is not a strict FIFO contract. A single overweight entry may exceed the limit until eviction maintenance runs. `removeIf()` iterates a live concurrent view and may race with updates.

## Test Signals
`TestResourceCache` exercises weighted eviction and removal behavior. Additional useful tests are listener invocation, null-argument checks, overweight entries, and concurrent `removeIf()` with puts.
