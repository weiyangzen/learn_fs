# sources/storage-engines/tikv/components/backup-stream/src/tempfiles.rs

## Purpose
`tempfiles.rs` implements backup-stream's local temporary file pool. It offers appendable write handles that keep data in memory until a quota/threshold triggers spill to disk, optional compression for logical file content, optional local spill-file encryption through TiKV's data key manager, raw read handles for uploading the compressed bytes, and cleanup of memory/disk resources.

The module exists because backup-stream writes many small log fragments before flushing them to external storage. It reduces disk IO by buffering small files, spills larger files when memory pressure requires it, and preserves retryability by allowing a completed temp file to be read multiple times until the caller explicitly removes it.

## Important APIs, Types, And Functions
`Config` controls `cache_size`, `swap_files` directory, `content_compression`, `minimal_swap_out_file_size`, and `write_buffer_size`. `TempFilePool::new()` initializes the swap directory, deleting any existing content with encryption-aware removal when needed. `TempFilePool::open_for_write()`, `open_raw_for_read()`, `remove()`, `config()`, and test-only `mem_used()` are the main pool APIs.

`TempFilePool` stores current in-memory capacity usage, a mutex-protected `FileSet`, and a `BackupEncryptionManager`. `FileSet` maps relative paths to `File`, which contains shared `FileCore` and atomic reader/writer counts.

`ForWrite` is either `ZstdCompressed(ZstdCompressionWriter<ForWriteCore>)` or `Plain(ForWriteCore)` and implements `AsyncWrite` plus the crate `CompressionWriter::done()`. `ForWriteCore` owns write state for one file path and closes/syncs spill files in `done()`. `ForRead` implements `AsyncRead` over a file's swapped-out prefix plus in-memory tail and exposes `len()`.

`FileCore` contains the in-memory buffer, optional `SwappedOut` writer, count of in-memory bytes already written to disk, owning pool, and relative path. Key methods are `should_swap_out()`, `poll_swap_out_unpin()`, `append_to_buffer()`, `max_cache_size()`, and `new()`. `SwappedOut` abstracts plain Tokio files, encrypted writers, test dynamic writers, and closed state; it implements `AsyncWrite` and `done()`.

Helper `modify_and_update_cap_diff()` updates a `Vec<u8>` and adjusts the pool memory counter by capacity delta, updating `TEMP_FILE_MEMORY_USAGE`.

## Control Flow
`TempFilePool::new()` treats the swap directory as scratch. If the directory already exists, it logs and removes it recursively, using the data key manager when configured, then recreates it. This makes restart after panic clear leaked temp files rather than reusing stale content.

`open_for_write()` locks the file map, creates a new `FileCore` for the relative path if absent, rejects writes while reader count is nonzero, increments writer count, wraps the `ForWriteCore` in zstd compression if configured, and returns the write handle. Multiple writers are counted, but the router's usage normally has one writer per temp file. `open_raw_for_read()` rejects reads while writer count is positive, opens the swapped file for decrypted raw read if the file has spilled, increments reader count, and returns a `ForRead` cursor.

`ForWriteCore::poll_write()` rejects writes after `done()`, locks `FileCore`, calls `should_swap_out(buf.len())`, and if true drives `poll_swap_out_unpin()` before appending the new bytes to the in-memory buffer. `should_swap_out()` triggers spill when an upcoming reallocation would exceed the memory quota and the file is large enough, when an already spilled file has accumulated more than the write buffer, or when a previous spill has a partial write in progress. `poll_swap_out_unpin()` lazily creates the relative disk file, repeatedly writes `in_mem[written..]`, advances `written`, records swap metrics, then clears and shrinks the memory buffer to the configured write buffer size and resets `written`.

`CompressionWriter::done()` on `ForWrite` first finalizes the zstd writer when present, then calls `ForWriteCore::done()`. `ForWriteCore::done()` is idempotent from the caller's perspective: it caches success or stringified failure in `done_result`. If an external spill file exists, it uses `spawn_blocking()` to lock the core, replace the external writer with `Closed`, call `SwappedOut::done()`, and sync the underlying file. It decrements writer count after attempting closure.

`ForRead::poll_read()` first reads from the decrypted external file if this is the beginning of the read and a spill file exists. When that external file reaches EOF, it reads from the current in-memory buffer starting at `read`. `ForRead::len()` reports disk metadata length plus retained in-memory tail. Dropping `ForRead` decrements reader count. Dropping `ForWriteCore` decrements writer count if `done()` was never called.

`TempFilePool::remove()` removes the map entry and decrements `TEMP_FILE_COUNT`; actual disk cleanup happens when the last `Arc` to `FileCore` drops. `FileCore::drop()` subtracts the buffer capacity from the memory counter and deletes the relative spill file if one exists. This delayed cleanup allows existing readers/writers to finish after pool removal.

## State And Persistence Behavior
The pool's state is intentionally temporary. It may hold file content entirely in memory, partly in a local swap file and partly in memory, or entirely in a local swap file after `done()`. The local swap directory is cleared on pool creation, so content is not persisted across process restart for recovery. Backup durability is supplied later by router upload to external storage.

Within a live process, `done()` provides local spill-file synchronization for files that have been swapped out. Purely in-memory files have no local fsync. `open_raw_for_read()` returns compressed/encrypted-spill-decoded raw content as the router expects to upload compressed bytes to external storage; it does not decompress zstd content.

Local spill encryption uses `backup_encryption_manager.opt_data_key_manager()`. `create_relative()` wraps new spill writers with encrypted writers when available; `open_relative()` wraps readers with decrypting readers or plaintext decryptors; `delete_relative()` delegates encrypted file deletion before removing the OS file. This is separate from external backup-object encryption in `router.rs`.

Memory accounting tracks vector capacity, not logical bytes, through `current`. Shrinking after spill reduces the tracked capacity to the write buffer size. The `cache_size` is an atomic so router config updates can change quota for an existing pool.

## Dependencies And Integration Points
This module depends on Tokio `AsyncRead`/`AsyncWrite`, `async_compression` through the crate's `ZstdCompressionWriter`, encryption crate readers/writers and `BackupEncryptionManager`, `kvproto` compression and encryption enums, TiKV metrics, failpoints, and crate error/annotation utilities.

`router.rs` is the primary consumer: it creates a `TempFilePool` per stream task, opens `ForWrite` handles for `DataFile`s, calls `done()` before flush, opens `ForRead` with `open_raw_for_read()` to merge/upload compressed temp content, and calls `remove()` after successful metadata upload or task drop. Config updates mutate the pool's `cache_size` atomic through `RouterInner::update_config()`.

## Risks And Edge Cases
The file uses synchronous `std::sync::Mutex` inside async `poll_*` implementations. The code keeps critical sections small, but `poll_swap_out_unpin()` polls an async writer while holding the mutex, which can be risky if future writer implementations call back into the same state. The comments acknowledge implementation complexity around async mutexes and polling.

Concurrent access rules are strict: reads are rejected while writers exist, and writes are rejected while readers exist. Writer count correctness depends on `done()` and `Drop` paths; double decrement would allow unsafe reads, while missed decrement would permanently block reads. `ForWriteCore::done()` caches failures because retrying finalization after ownership-consuming writers may be impossible; a failed `done()` can make the task eventually fail and may represent data loss for that temp file.

`ForRead::poll_read()` only reads from the external file while `read == 0`; after any in-memory bytes are read, it will not return to the file. This matches the invariant that the spill file contains the prefix and memory contains the tail, but changes to partial-read logic could break ordering. `len()` uses `st.in_mem.len() - st.written`; after successful spill `written` resets to zero and the in-memory buffer is the tail.

`modify_and_update_cap_diff()` only updates metrics when `diff > 0`, but `diff` is a wrapping subtraction, so shrinkage produces a huge positive wrapped value and relies on atomic wrapping arithmetic to subtract capacity. This is clever but fragile for maintainers. Existing swap directory deletion on pool creation is correct for scratch state, but a misconfigured `swap_files` path could delete unexpected directory contents.

Unsupported compression returns an error from `open_for_write()`. Small files below `minimal_swap_out_file_size` may remain in memory even when quota is tight. The failpoints can override cache size or force swapout, which is useful for tests but must be scoped carefully.

## Test Signals
Tests cover the core invariants. `test_read` validates in-memory reads. `test_swapout` validates spill threshold behavior and combined disk+memory reads. `test_compression` writes zstd content, reads raw, and decompresses to original bytes. `test_write_many_times` uses a dynamic writer that only writes two bytes at a time to validate partial-write spill loops. `test_read_many_times` validates retry reads and write reopening after readers drop. `test_not_leaked` validates memory and disk cleanup after remove. `test_panic_not_leaked` validates stale swap directory cleanup on new pool creation. `test_various_encryption` validates encrypted spill files for AES and SM4 modes and confirms on-disk content is not plaintext while readback matches.

Additional useful tests would cover reader/writer rejection errors, `done()` failure caching, unsupported compression, dynamic quota updates, exact memory counter behavior on growth and shrink, encrypted delete failure, and a misconfigured swap path guard at higher configuration layers.
