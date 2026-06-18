# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompressionTypesTest.java

## Purpose

Validates string-to-enum lookup for compression library names.

## Important APIs, control flow, and dependencies

The test iterates all `CompressionType` values, calls `getLibraryName`, then resolves it through `CompressionType.getCompressionType`. The sentinel `DISABLE_COMPRESSION_OPTION` is expected to resolve to `NO_COMPRESSION`.

## State, persistence, risks, and test signals

No native DB state is involved. The risk is lookup drift for names used in option parsing or metadata. Signals are exact enum equality for each library name and the special sentinel behavior.
