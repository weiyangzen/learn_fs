# sources/storage-engines/raft-engine/src/env/mod.rs

## Purpose
Defines raft-engine's filesystem abstraction layer so the engine can run over default, test, obfuscated, or user-provided file systems.

## Important APIs, Types, And Functions
Exports `DefaultFileSystem` and `ObfuscatedFileSystem`. Defines `Permission`, trait `FileSystem`, trait `Handle`, and trait `WriteExt`.

## Control Flow
`FileSystem` implementors provide create/open/delete/rename, optional reuse/reuse-and-open, metadata cleanup hooks, and reader/writer construction. `Handle` provides truncate, file-size, and sync. `WriteExt` provides writer-side truncate and allocation. Default `reuse` is rename, and default metadata hooks are no-ops.

## State And Persistence Behavior
The abstraction is the persistence boundary for log files and associated external metadata. Metadata hooks support cleanup for older versions that deleted physical files without invoking user metadata cleanup.

## Dependencies And Integration Points
Used by `Engine`, `FilePipeLog`, file readers/writers, test file systems, CLI injection, and examples. `Permission` maps into platform open flags in backend modules.

## Risks And Edge Cases
Implementors must preserve expected durability semantics for sync, truncate, rename/reuse, and metadata deletion. A filesystem whose `exists_metadata` disagrees with physical files can confuse recovery cleanup. Reuse semantics may be stronger or weaker than rename depending on implementation.

## Test Signals
The unit test verifies `Permission` copy/equality. Broader signals come from engine tests using `ObfuscatedFileSystem` and `DeleteMonitoredFileSystem`.
