# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryExtension.java

Purpose: synchronous directory-layer extension for the stack tester. It interprets `DIRECTORY_` stack operations and exposes Java directory/subspace behavior to cross-binding directory tests.

Important APIs and flow: `dirList` stores `DirectoryLayer`, `Directory`, `DirectorySubspace`, `Subspace`, or null handles addressed by stack-supplied indexes. `processInstruction` creates subspaces/layers, changes current handle, creates/opens/moves/removes directories, lists and checks existence, packs/unpacks/ranges subspace keys, logs directory metadata, and strips prefixes. It uses `DirectoryUtil` to pop tuple paths and pushes encoded results back onto the instruction stack.

State and persistence: directory metadata is persisted through `DirectoryLayer` under the configured node/content subspaces, and logging operations write to the active transaction. Error handling pushes `DIRECTORY_ERROR` and appends null for operations that would have produced a directory handle. Risks include blocking `.get()` calls, null handle fallback through `errorIndex`, compatibility hacks around `exists` read versions, and preserving handle order exactly for cross-binding scripts.
