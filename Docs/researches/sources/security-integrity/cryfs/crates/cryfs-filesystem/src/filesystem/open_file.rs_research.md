# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/open_file.rs

## Purpose
Implements `CryOpenFile`, the RustFS open-file adapter for reading, writing, flushing, fsyncing, and changing attributes on file blobs.

## Important APIs, types, and functions
- `CryOpenFile::new` owns blobstore and shared `NodeInfo` guards.
- `load_blob` and `as_file_mut` load/cast the underlying blob.
- `_read`, `_write`, and `flush_file_contents` perform file-data operations.
- The `OpenFile` trait impl provides `getattr`, `setattr`, `read`, `write`, `flush`, and `fsync`.

## Control flow
Reads allocate a `Data` buffer of requested size, call `try_read`, and shrink to bytes actually read. Non-zero reads run concurrently with parent atime updates. Writes call `FileBlob::write`; non-empty writes run concurrently with parent mtime updates. `flush` currently delegates to full `fsync(false)` for parity with the former C++ behavior. `fsync(true)` flushes file contents only; `fsync(false)` flushes file contents and parent metadata in parallel.

## State and persistence behavior
File contents and size persist in the file blob. Access and modification times persist in the parent directory entry through `NodeInfo`. Full fsync persists both content and metadata; datasync mode skips parent metadata.

## Dependencies and integration points
Depends on `cryfs_utils::data::Data`, `ConcurrentFsBlobStore`, `FileBlob`, `FsBlob`, RustFS `OpenFile`, and shared `NodeInfo`. It is created from `CryFile::into_open` and `CryDir::create_and_open_file`.

## Risks and edge cases
Large reads allocate the full requested size before knowing available data. `data.len() > 0` and `size > 0` control timestamp behavior, so zero-length IO intentionally avoids timestamp updates. `flush` doing fsync may be more expensive than expected. Casting failures are logged and sometimes remapped to `UnknownError`, losing corruption detail.

## Test signals
Expected signals include read/write round trips, short reads, zero-length IO timestamp behavior, fsync datasync vs full behavior, flush-on-close behavior, truncate through setattr, and corrupted file blob type handling.
