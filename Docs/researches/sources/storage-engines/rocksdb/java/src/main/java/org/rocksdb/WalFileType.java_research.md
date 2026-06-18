# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WalFileType.java

## Purpose
`WalFileType` describes whether a WAL file is archived or live. It is a small JNI-facing enum used when exposing WAL file metadata.

## Important APIs and Types
Values are `kArchivedLogFile` and `kAliveLogFile`. Package-private `getValue()` returns the native byte and `fromValue(byte)` converts bytes to enum constants.

## Control Flow, State, and Persistence
There is no runtime control flow beyond conversion. The enum describes persistent WAL file location/lifecycle: live logs are in the DB directory, while archived logs are retained under archive cleanup policies.

## Dependencies and Integration Points
It integrates with WAL file metadata APIs elsewhere in the RocksDB Java binding and must match native constants.

## Risks and Test Signals
Unknown byte values fail with `IllegalArgumentException`. This subset has no direct WAL file metadata tests.
