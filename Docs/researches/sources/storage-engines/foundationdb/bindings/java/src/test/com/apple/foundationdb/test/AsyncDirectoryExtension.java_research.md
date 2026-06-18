<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java

## Purpose
`AsyncDirectoryExtension` implements asynchronous stack-machine instructions for testing the Java directory and subspace APIs against binding conformance scenarios.

## Important APIs, Types, And Functions
It stores a list of directory/subspace handles, active `dirIndex`, and `errorIndex`. `processInstruction` wraps `executeInstruction` and reports failures through test `DirectoryUtil.pushError`. `executeInstruction` handles `DirectoryOperation` values for creating subspaces/layers, changing current directory, create/open/create, move, remove, list, exists, pack/unpack/range/contains, open subspace, log subspace/directory, and strip prefix.

## Control Flow
Each instruction pops typed values from `Instruction`, calls the selected async directory/subspace method, and pushes outputs back to the stack. Errors are converted to stack-test errors instead of escaping. `DIRECTORY_EXISTS` forces a read version first because Java's root `DirectoryLayer.exists` can otherwise return true without reading, while other bindings perform a read.

## State And Persistence Behavior
`dirList` persists handles across instructions. Some instructions write to the database, especially directory mutations and log operations that store path/layer/exists/children under tuple-packed log keys. Directory state itself is persisted by `DirectoryLayer`.

## Dependencies And Integration Points
It depends on `Instruction`, `DirectoryOperation`, test `DirectoryUtil`, `StackUtils`, `AsyncUtil`, `Directory`, `DirectoryLayer`, `DirectorySubspace`, `Subspace`, `Tuple`, and `Range`. It complements synchronous `DirectoryExtension` and cross-binding stack tests.

## Risks And Test Signals
Risks include type casts from stack parameters, null handle handling through `errorIndex`, async exception wrapping hiding exact failure points, path count conventions for remove/list/exists, and compatibility quirks such as forced read versions. Tests should execute every directory opcode, compare async and sync extension behavior, cover null/error index paths, and validate logged directory metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java -->
