# sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.h

## Purpose
This header declares the simulated hybrid file system used by benchmark/development tooling. It exposes wrappers for a `FileSystem`, random-access files, and writable files that can inject warm-storage latency and rate limiting.

## Important APIs, Types, and Functions
`SimulatedHybridFileSystem` derives from `FileSystemWrapper` and overrides `NewRandomAccessFile`, `NewWritableFile`, `DeleteFile`, and `Name`. It stores a `RateLimiter`, mutex, warm file set, metadata filename, display name, and full-FS-warm flag. `SimulatedHybridRaf` derives from `FSRandomAccessFileOwnerWrapper` and overrides `Read`, `MultiRead`, and `Prefetch`. `SimulatedWritableFile` derives from `FSWritableFileWrapper` and overrides append, positioned append, and `Sync`.

## Control Flow
The declarations establish a wrapping design: the file system decides whether a file is warm and returns wrappers; the file wrappers call private `SimulateIOWait()` before delegating to the target file. Writable files distinguish direct I/O, which waits per append, from buffered I/O, which accumulates bytes until sync.

## State and Persistence
The file system owns warm-file membership and a metadata filename for cross-run persistence. Random-access wrappers hold immutable temperature state. Writable wrappers hold the owned target file and an `unsynced_bytes` accumulator.

## Dependencies and Integration Points
It includes `rocksdb/file_system.h` and uses RocksDB `Temperature`, `RateLimiter`, `IOOptions`, `FileOptions`, and `IODebugContext` types. It is meant to be plugged into RocksDB options/env configuration for benchmark runs.

## Risks
The header notes this is development-only and should not be used in production. Thread-safety is limited to warm-set management; per-file accumulators are not externally synchronized. Consumers must understand that warm classification changes I/O latency and may persist between runs through metadata.

## Test Signals
Signals come from the implementation and benchmark behavior: wrapped warm reads/writes should be slower, deletion should remove warm metadata, and reopening with metadata should restore warm classification.
