# sources/storage-engines/rocksdb/include/rocksdb/utilities/table_properties_collectors.h

## Purpose
Declares table-property collector factories for deletion/tiering compaction triggers and helpers for data Unix write-time statistics.

## Important APIs, Types, And Functions
`CompactOnDeletionCollectorFactory`, `NewCompactOnDeletionCollectorFactory`, `CompactForTieringCollectorFactory`, `NewCompactForTieringCollectorFactory`, `DataCollectionUnixWriteTimeInfo`, `GetDataCollectionUnixWriteTimeInfoForFile`, and `GetDataCollectionUnixWriteTimeInfoForLevels`.

## Control Flow, State, And Persistence
Collectors observe table building and mark files needing compaction or write user properties based on atomic thresholds. Write-time helpers decode table properties for files/levels. Collector thresholds are runtime atomics; outputs persist in SST properties/metadata.

## Dependencies And Integration Points
Depends on `TablePropertiesCollectorFactory`, `TableProperties`, `SystemClock`, and `Status`. Integrates with table building, compaction picking, tiering, and property inspection.

## Risks And Edge Cases
Deletion ratios outside `(0,1]` disable ratio triggering. Window sizes may be rounded by factory creation. File-size estimates can be approximate during table building. Tiering collector is disabled for non-tiering CFs. Write-time stats require checking tracked-data ratio before interpreting values.

## Test Signals
Cover tombstone-window and ratio triggers, disabled settings, minimum file size, dynamic setters, tiering properties, write-time extraction, empty/untracked data, level aggregation, and string output.
