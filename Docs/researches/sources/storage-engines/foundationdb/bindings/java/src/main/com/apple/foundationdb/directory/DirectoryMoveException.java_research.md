<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java

## Purpose
`DirectoryMoveException` represents invalid directory move requests, such as moving root, moving into a descendant, or crossing partition boundaries.

## Important APIs, Types, And Functions
It extends `RuntimeException`, exposes `sourcePath` and `destPath`, and formats both paths with `DirectoryUtil.pathStr`.

## Control Flow, State, And Persistence
It is constructed synchronously or during async composition before any valid move mutation is completed. The object records source and destination path references.

## Dependencies And Integration Points
`DirectoryLayer.moveTo`, `DirectoryLayer.move`, and `DirectorySubspace.moveTo` use this class to report invalid move shapes. It is documented on the `Directory` interface.

## Risks And Test Signals
The source/destination lists are not defensively copied. Tests should trigger root move, self-subtree move, and cross-partition move, then assert class, message, and path fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java -->
