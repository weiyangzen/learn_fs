# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFilter.java

## Purpose
`TableFilter` is a Java callback interface that lets scans decide whether a table should be scanned based on `TableProperties`.

## Important APIs and Types
It declares one method: `boolean filter(TableProperties tableProperties)`.

## Control Flow
During iterator/table scan setup, native or Java bridge code can call `filter` with each table's properties. Returning `false` skips that table for iterator scans; point lookups are unaffected.

## State and Persistence Behavior
The interface has no state. Implementations may carry arbitrary state, but the filter itself only influences read-path table selection.

## Dependencies and Integration Points
It depends on `TableProperties` and is used by read/iterator options that support table-level filtering.

## Risks and Test Signals
Tests should verify that filters skip iterator table access, do not affect point lookups, receive correct table properties, and propagate callback exceptions as expected. Implementations must be efficient because they can run on scan setup paths.
