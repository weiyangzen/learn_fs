
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/mod.rs

## Purpose
`OnDiskBlockStore` persists low-level blocks as files under a base directory. It adds a small block-file format header, shards file paths by the first three uppercase hex characters of the block id, and implements the low-level reader/deleter/optimized-writer traits.

## Important APIs, Types, and Functions
- `OnDiskBlockStore::new(basedir)` constructs an async-drop guarded store.
- `FORMAT_VERSION_HEADER_PREFIX` is `cryfs;block;`; `FORMAT_VERSION_HEADER` is `cryfs;block;0\0`.
- `PREFIX_LEN = 3`; `NONPREFIX_LEN = 2 * BLOCKID_LEN - PREFIX_LEN`.
- `exists`, `load`, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks` implement `BlockStoreReader`.
- `remove` deletes a block file and maps `NotFound` to `NotRemovedBecauseItDoesntExist`.
- `allocate`, `try_create_optimized`, and `store_optimized` implement prefix-capable writes.
- `_all_block_files()` streams valid sharded block files while skipping unrelated entries.
- `_blockid_from_filepath()` reconstructs ids from matching paths.
- `_check_and_remove_header()` validates and strips the file-format header.
- `_store()` creates parent directories, prepends the file header, and writes the file.
- `_block_path()` maps ids to uppercase hex `basedir/ABC/DEF...` paths.

## Control Flow
Reads compute the block path, read the whole file with `tokio::fs::read`, map missing files to `Ok(None)`, validate the header, shrink the `Data` region past the header, and return user data. Writes allocate with reserved prefix bytes, grow the region to include the header without reallocation, copy the header, and write the whole file. `try_create_optimized()` performs an existence check before writing; it is not atomic against concurrent creators. Listing reads the base directory, filters three-character uppercase-hex subdirs, flattens their entries, then filters blockfile-name length and uppercase-hex characters.

## State and Persistence Behavior
Each block is a file. Parent sharding directories are created lazily and not removed on delete. The store has no async-drop cleanup and no open file handles. Free-space estimation delegates to the platform-specific `sysinfo` module for the filesystem containing `basedir`.

## Dependencies and Integration Points
The module depends on Tokio filesystem APIs, `tokio_stream::wrappers::ReadDirStream`, `base64` for invalid-block diagnostics, `byte_unit::Byte`, CryFS `Data`, and `path_join`. It is often wrapped by integrity, encryption, compression, or tempdir stores.

## Risks and Edge Cases
- `try_create_optimized()` uses check-then-write and can race under concurrent writers.
- `_blockid_from_filepath()` panics on invalid assumptions; it is only called after stream filters.
- Header errors include base64-encoded block contents, which can be large.
- `_create_dir_if_doesnt_exist()` uses `create_dir` rather than recursive creation; callers assume `basedir` already exists.
- Lowercase hex files are not read; TODO notes possible future lowercase migration with uppercase fallback.
- Windows free-space support lives in `sysinfo.rs` and appears suspicious there.

## Test Signals
Tests instantiate the common low-level suite, validate block path generation, assert header prefix relationship, check overhead conversion, compare physical file size to usable size, verify files appear after store, and verify files disappear after remove.
