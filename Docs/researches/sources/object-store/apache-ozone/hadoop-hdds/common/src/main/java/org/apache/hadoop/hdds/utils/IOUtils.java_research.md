# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/IOUtils.java

## Purpose
Static IO and closeable helpers for cleanup, quiet/error logging close operations, atomic properties persistence, file inode lookup, and chunk-size rounding.

## Important APIs and types
`cleanupWithLogger` catches `Throwable` and logs debug for exception-handler cleanup. `close` logs `Exception` at error level. `closeQuietly` delegates with no logger. `writePropertiesToFile` uses `AtomicFileOutputStream`. `readPropertiesFromFile` loads Java properties. `getINode` returns `BasicFileAttributes.fileKey()`. `roundUp` rounds a required size to a chunk multiple and asserts bounds.

## Control flow and state
All methods are stateless. Close helpers tolerate null collections and null elements. `writePropertiesToFile` truncates via atomic-file semantics provided by Ratis. `roundUp` computes `(requiredSize - 1) / chunkSize`, so zero or invalid chunk sizes require caller discipline.

## Dependencies and integration points
Depends on Java IO/NIO, Jakarta `Nonnull`, Ratis `AtomicFileOutputStream` and `Preconditions`, and SLF4J `Logger`.

## Risks and test signals
Tests should cover close exception logging behavior, null handling, atomic property round trips, inode availability differences by filesystem, and `roundUp` boundaries including exact multiples. `cleanupWithLogger` catches `Throwable`, so use only in cleanup paths as documented.
