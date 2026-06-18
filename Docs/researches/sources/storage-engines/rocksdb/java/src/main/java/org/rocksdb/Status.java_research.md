# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Status.java

## Purpose
`Status` is the Java serializable representation of RocksDB native status values, primarily attached to `RocksDBException`.

## Important APIs and Types
The class stores `Code`, optional `SubCode`, and optional state string. Public APIs are getters, `getCodeString()`, `equals`, and `hashCode`. `Code` maps high-level status values such as `Ok`, `NotFound`, `Corruption`, `InvalidArgument`, `IOError`, `Busy`, `TimedOut`, and `TryAgain`. `SubCode` maps more specific causes such as `LockTimeout`, `NoSpace`, `Deadlock`, `StaleFile`, and `MemoryLimit`.

## Control Flow
JNI can construct status through a private byte-based constructor that calls `Code.getCode` and `SubCode.getSubCode`. Reverse mapping methods linearly scan enum values and throw for unknown bytes. `getCodeString` appends a non-`None` subcode in parentheses.

## State and Persistence Behavior
The object is immutable and serializable. It does not persist native state; it snapshots status information into Java fields.

## Dependencies and Integration Points
It integrates with `RocksDBException` and many transactional/event DTOs such as `TableFileCreationInfo` and `TableFileDeletionInfo`. Comments explicitly require synchronization with native `status.h` and JNI portal mapping.

## Risks and Test Signals
Tests should cover byte mappings, serialization compatibility, null subcodes, code-string formatting, equality, and behavior for future native codes. The main risk is enum drift between Java, native headers, and JNI conversion code.
