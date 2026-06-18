# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestResourceCache.java

## Purpose
Tests `ResourceCache` lifecycle behavior: caching, removal, conditional removal, and clearing with cleanup callbacks.

## Important APIs, types, and functions
- Uses `ResourceCache`, `AtomicLong`, and `Consumer` cleanup callbacks.
- Test cases include `testResourceCache`, `testRemove`, `testRemoveIf`, and `testClear`.

## Control flow
Tests request resources by key, verify cache hits reuse existing resources, remove specific entries or entries matching predicates, and assert cleanup counters/callbacks run for evicted resources.

## State and persistence behavior
The cache is an in-memory map of keys to resources plus cleanup side effects. No persistence.

## Dependencies and integration points
Resource caching supports shared expensive objects in HDDS utilities while ensuring deterministic cleanup.

## Risks and test signals
Bugs can leak resources or prematurely close shared ones. Tests signal reuse and cleanup behavior for each eviction path.
