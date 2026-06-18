# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableFileCreationReason.java

## Purpose
`TableFileCreationReason` maps native reasons for SST/table-file creation into Java enum values.

## Important APIs and Types
Values are `FLUSH`, `COMPACTION`, `RECOVERY`, and `MISC`. Package-private `getValue()` returns the native byte and static `fromValue(byte)` performs reverse mapping.

## Control Flow
Reverse mapping scans enum values and throws `IllegalArgumentException` on unknown bytes.

## State and Persistence Behavior
There is no mutable state. Values describe why persistent table files were created but do not manage files.

## Dependencies and Integration Points
`TableFileCreationBriefInfo` and `TableFileCreationInfo` use it when converting native event payloads.

## Risks and Test Signals
Tests should verify all mappings and failure behavior for unknown native values. Native additions must be mirrored here or Java event construction can fail.
