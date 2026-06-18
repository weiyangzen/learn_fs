# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalProcessingOption.java

## Purpose
`WalProcessingOption` enumerates possible recovery actions returned by a `WalFilter`.

## Important APIs and Types
Values are `CONTINUE_PROCESSING`, `IGNORE_CURRENT_RECORD`, `STOP_REPLAY`, and `CORRUPTED_RECORD`, each with a native byte. Package-private `getValue()` and public `fromValue(byte)` bridge JNI.

## Control Flow, State, and Persistence
The enum itself is immutable. In recovery, these values decide whether WAL replay proceeds, skips a record, discards logs from the current point onward, or treats the record as corrupt.

## Dependencies and Integration Points
Used by `WalFilter.LogRecordFoundResult` and native recovery callbacks. Constants must stay byte-aligned with RocksDB C++.

## Risks and Test Signals
`STOP_REPLAY` has destructive recovery semantics because subsequent logs are discarded. Unknown byte conversion fails fast. This subset includes no direct test for these options.
