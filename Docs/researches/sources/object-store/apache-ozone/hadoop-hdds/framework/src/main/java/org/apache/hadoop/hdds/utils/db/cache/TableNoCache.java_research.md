# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/cache/TableNoCache.java

## Purpose

`TableNoCache` is a singleton no-op cache implementation for tables that should always consult RocksDB on cache misses. The complete 101-line source was read for this report.

## Important APIs, Types, and Functions

It exposes `instance()` and implements all `TableCache` methods as no-ops or empty values. `lookup` returns `MAY_EXIST`; `getStats` returns static `EMPTY_STAT`; `getCacheType` returns `NO_CACHE`.

## Control Flow

All mutation and cleanup methods do nothing. Lookup never says a key is absent or present, forcing `TypedTable` to fall through to the raw table.

## State and Persistence Behavior

There is no cache state. Persistence is entirely delegated to the backing table.

## Dependencies and Integration Points

It is used by `TypedTable` when the cache type is neither full nor partial. It depends on Java empty collections and cache wrapper types.

## Risks and Edge Cases

Unchecked singleton casts are safe only because the implementation holds no typed values. Callers expecting cache iteration or size will always see empty results.

## Test Signals

Tests should verify singleton behavior, all methods being inert, `MAY_EXIST` lookup, empty stats, and `TypedTable` DB fallback under no-cache mode.
