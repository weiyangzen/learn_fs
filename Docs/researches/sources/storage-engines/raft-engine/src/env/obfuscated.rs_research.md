# sources/storage-engines/raft-engine/src/env/obfuscated.rs

## Purpose
Implements a special test filesystem that transforms bytes on read/write and tracks file counts, helping catch assumptions about direct filesystem contents and file lifecycle.

## Important APIs, Types, And Functions
`ObfuscatedReader`, `ObfuscatedWriter`, and `ObfuscatedFileSystem` implement the file abstraction. `file_count` reports the tracked count of successfully created minus deleted files.

## Control Flow
The reader reads at most one byte and subtracts one from it before returning. The writer writes at most one byte, adding one first. Seeks, truncate, and allocate delegate to the default implementation. `ObfuscatedFileSystem` delegates create/open/delete/rename/new_reader/new_writer to `DefaultFileSystem`, increments count on successful create, decrements on successful delete, and implements `reuse` as delete plus create.

## State And Persistence Behavior
The on-disk bytes are intentionally obfuscated relative to logical bytes. File count is in-memory atomic state used by tests to validate deletion/reuse behavior. Durable data is still stored through the default filesystem.

## Dependencies And Integration Points
Used heavily in engine tests to run through the generic `FileSystem` abstraction. It depends on `DefaultFileSystem`, `Permission`, `WriteExt`, and atomics.

## Risks And Edge Cases
One-byte read/write behavior stresses callers that assume full-buffer progress. It is not a production filesystem and has different reuse semantics from rename-based filesystems.

## Test Signals
Engine recovery, rewrite, purge, and read tests using this filesystem signal that higher layers tolerate short I/O and abstract byte transformations.
