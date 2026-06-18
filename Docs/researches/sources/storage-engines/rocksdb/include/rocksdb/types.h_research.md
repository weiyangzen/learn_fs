# Research: sources/storage-engines/rocksdb/include/rocksdb/types.h

- **Purpose:** Centralizes public lightweight RocksDB type aliases and enums shared across headers.
- **Important APIs/types/functions:** Defines `ColumnFamilyId`, `SequenceNumber`, `TablePropertiesCollection`, `kMinUnCommittedSeq`, `TableFileCreationReason`, `BlobFileCreationReason`, `FileType`, `EntryType`, `ParsedEntryInfo`, `WriteStallCause`, `WriteStallCondition`, and file `Temperature`.
- **Control flow:** These are consumed as classification and identity values across APIs. `ParsedEntryInfo` provides user key, optional timestamp, sequence number, and entry type when exposing internal entries.
- **State and persistence:** Several values correspond to durable concepts: WAL sequence numbers, file types in DB directories, table/blob creation reasons, internal key entry types, and tiered-storage temperatures. Comments warn enum ordering for `EntryType` should not change.
- **Dependencies:** Depends on `Slice` and forward-declared `TableProperties`.
- **Integration points:** Used by table properties, transaction logs, compaction/tiering, file-system placement, write-stall reporting, and public metadata APIs.
- **Risks:** Changing enum values can break API compatibility or persisted/diagnostic interpretation. `Temperature::kLastTemperature` is explicitly misnamed as an invalid sentinel, so code should not treat it as a real tier.
- **Test signals:** Tests should validate enum conversion/display code elsewhere, sequence-number edge cases, timestamp parsing with and without user-defined timestamps, and write-stall/temperature mapping.
