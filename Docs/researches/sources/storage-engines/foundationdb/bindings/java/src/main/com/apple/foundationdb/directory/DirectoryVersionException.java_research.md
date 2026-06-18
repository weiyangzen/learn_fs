<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java

## Purpose
This runtime exception reports incompatible on-database directory-layer metadata versions.

## Important APIs, Types, And Functions
`DirectoryVersionException` extends `RuntimeException` with a package-private message constructor.

## Control Flow, State, And Persistence
`DirectoryLayer.VersionCheck` throws it when the stored major version is newer than the binding supports. `WritableVersionCheck` also throws when the stored minor version is newer for write operations, making the layer read-only.

## Dependencies And Integration Points
It is tied to `DirectoryLayer.VERSION` and the `rootNode/version` metadata key. It protects Java clients interacting with directories created by newer bindings.

## Risks And Test Signals
Tests should seed version metadata for equal, newer patch, newer minor, and newer major versions to verify read/write compatibility behavior and error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java -->
