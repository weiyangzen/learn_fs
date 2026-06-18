<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java

## Purpose
This exception reports opening an existing directory with a non-empty expected layer byte string that differs from the stored layer.

## Important APIs, Types, And Functions
It extends `DirectoryException` and exposes `stored` and `opened` byte arrays. The message uses `ByteArrayUtil.printable` for binary-safe layer rendering.

## Control Flow, State, And Persistence
`DirectoryLayer.openInternal` throws it when `layer.length > 0` and arrays differ. Empty expected layer acts as no layer check.

## Dependencies And Integration Points
It is part of the `Directory.open` and `createOrOpen` contract and depends on `ByteArrayUtil` for diagnostics.

## Risks And Test Signals
The byte arrays are stored by reference, so caller mutation can affect fields. Tests should cover matching layers, empty expected layer, mismatched binary layer bytes, and async exceptional completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java -->
