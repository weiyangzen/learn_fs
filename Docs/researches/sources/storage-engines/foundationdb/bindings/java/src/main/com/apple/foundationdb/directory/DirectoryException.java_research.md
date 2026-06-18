<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java

## Purpose
`DirectoryException` is the base runtime exception for directory-layer failures that correspond to a specific path.

## Important APIs, Types, And Functions
It extends `RuntimeException`, exposes a public final `List<String> path`, and has a package-private constructor combining a base message with `DirectoryUtil.pathStr(path)`.

## Control Flow, State, And Persistence
There is no persistence. State is the path reference and formatted message. The class deliberately does not defensively copy the list, so callers should avoid mutating paths after exception construction.

## Dependencies And Integration Points
Subclasses include `DirectoryAlreadyExistsException`, `NoSuchDirectoryException`, and `MismatchedLayerException`. `DirectoryLayer` throws this base class directly for invalid root removal.

## Risks And Test Signals
Risk centers on mutable `path` aliasing and package-private construction limiting external specialization. Tests should check exception class, message path formatting, and path field contents from failing directory operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java -->
