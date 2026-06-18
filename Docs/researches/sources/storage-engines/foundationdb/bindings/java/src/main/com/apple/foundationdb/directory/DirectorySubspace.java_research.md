<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java

## Purpose
`DirectorySubspace` combines a normal tuple `Subspace` for directory contents with a `Directory` handle for operations relative to the path used to open it.

## Important APIs, Types, And Functions
It stores `path`, `layer`, and `directoryLayer`; extends `Subspace`; implements all `Directory` operations by delegating to the backing layer after computing a partition-relative subpath. It overrides `toString`, `equals`, `hashCode`, `getPath`, `getLayer`, and `getDirectoryLayer`.

## Control Flow
Create/open/list/move delegate through `directoryLayer` using `getPartitionSubpath`. `moveTo`, `remove`, `removeIfExists`, and `exists` call `getLayerForPath` first so subclasses such as `DirectoryPartition` can redirect empty-path operations.

## State And Persistence Behavior
The object is a client-side handle. It holds an immutable-by-convention path and layer byte string, and its inherited `Subspace` prefix determines where content keys are packed. `getLayer` returns a copy, but the constructor stores the path list reference.

## Dependencies And Integration Points
It is returned by `DirectoryLayer` for ordinary directories and inherited by `DirectoryPartition`. It integrates with `PathUtil`, `ByteArrayUtil.printable`, `TransactionContext`, `ReadTransactionContext`, and `Subspace`.

## Risks And Test Signals
Risks include mutable path aliasing, partition path slicing errors, and equality depending on both layer identity and prefix. Tests should cover relative create/list/remove, `moveTo` absolute path validation, `getLayer` defensive copy, subspace packing inherited from `Subspace`, and partition subclass overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java -->
