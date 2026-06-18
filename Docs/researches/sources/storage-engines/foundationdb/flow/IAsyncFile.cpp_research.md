# sources/storage-engines/foundationdb/flow/IAsyncFile.cpp

## Purpose
Provides common `IAsyncFile` and `IAsyncFileSystem` helper implementations for zero-filling ranges and incrementally deleting files.

## Important APIs, Types, And Functions
`IAsyncFile::~IAsyncFile()` is defaulted. `IAsyncFile::zeroRange()` wraps `zeroRangeHelper()`, which writes a 1 MiB aligned buffer filled with a fixed byte. `IAsyncFileSystem::incrementalDeleteFile()` wraps `incrementalDeleteHelper()`, which deletes a file and then truncates/syncs an already-open handle in chunks.

## Control Flow
`zeroRangeHelper()` allocates a 1 MiB aligned buffer, writes chunks from offset to offset+length, yields between writes, and frees the buffer. `incrementalDeleteHelper()` checks existence, opens the file read/write uncached/unbuffered if present, records size, calls filesystem `deleteFile()`, then repeatedly truncates the open handle downward by knob-defined amounts, syncing and delaying between truncations.

## State And Persistence Behavior
`zeroRange()` mutates file contents. `incrementalDeleteFile()` removes the directory entry and gradually releases/truncates file storage through the open handle. Timing/chunk sizes come from `FLOW_KNOBS`.

## Dependencies And Integration Points
Depends on `IAsyncFile.h`, `Knobs`, `Platform`, actor coroutine support, `IAsyncFileSystem::filesystem()`, aligned allocation, `yield()`, and `delay()`.

## Risks And Edge Cases
`zeroRangeHelper()` does not use RAII for the aligned buffer, so an exception during write/yield would skip `aligned_free()` unless actor lowering guarantees cleanup elsewhere. Incremental delete assumes truncating after unlink/delete is useful on the platform and that the open handle remains valid. Negative or tiny knob values would be dangerous if not validated upstream.

## Test Signals
No local tests. Signals come from async file tests, storage-engine file deletion behavior, disk-space release observations, and simulation exercising `zeroRange()`.
