<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java

## Purpose
`Directory` is the public interface for objects managed by the FoundationDB directory layer. It models a hierarchical directory path, its layer byte string, and operations on itself or subdirectories.

## Important APIs, Types, And Functions
The interface exposes `getPath`, `getLayer`, and `getDirectoryLayer`, then asynchronous methods for `createOrOpen`, `open`, `create`, `moveTo`, `move`, `remove`, `removeIfExists`, `list`, and `exists`. Convenience default overloads use `DirectoryLayer.EMPTY_PATH` and `EMPTY_BYTES` for root-relative or no-layer cases. Methods return `CompletableFuture` and accept `TransactionContext` for writes or `ReadTransactionContext` for reads.

## Control Flow
Control flow is mostly declarative: defaults delegate to fuller overloads. Implementations are expected to resolve relative subpaths against the directory, open or create nodes, validate layers, and return `DirectorySubspace` handles.

## State And Persistence Behavior
This file defines the persistence contract rather than storing state itself. Creates record directory metadata and optional layer/prefix. Moves rewrite directory metadata without changing the physical content prefix. Removes clear directory metadata and contents, with warnings that previously opened clients can still write under an old prefix.

## Dependencies And Integration Points
`DirectoryLayer` implements the root behavior; `DirectorySubspace` implements directory-scoped behavior; `DirectoryPartition` specializes partition roots. Exception classes in this package are named in the API contract.

## Risks And Test Signals
Risks include misuse of root-relative versus absolute paths, layer mismatch handling, stale open handles after remove/move, and manual prefix collisions. Test signals should cover every overload family, error future propagation, read-only versus write transaction usage, partition delegation, and idempotent `removeIfExists`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java -->
