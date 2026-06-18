<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java

## Purpose
`NoSuchDirectoryException` reports operations against a directory path that does not exist.

## Important APIs, Types, And Functions
It extends `DirectoryException` with a package-private constructor and fixed base message `No such directory`.

## Control Flow, State, And Persistence
`DirectoryLayer` throws it from open, create-with-open-disallowed, move source lookup, move parent lookup, remove with `mustExist`, and list when a node is absent. No persistence occurs in the exception itself.

## Dependencies And Integration Points
It relies on `DirectoryException` for path storage and formatting and is documented by `Directory` methods.

## Risks And Test Signals
Tests should cover missing open/list/remove/move-source/move-parent and verify the path reported is absolute relative to the active layer or partition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java -->
