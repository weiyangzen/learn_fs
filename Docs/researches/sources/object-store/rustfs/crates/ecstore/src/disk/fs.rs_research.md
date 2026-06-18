# sources/object-store/rustfs/crates/ecstore/src/disk/fs.rs

## Purpose
`fs.rs` is a small filesystem shim for the disk layer. It provides cached Tokio `OpenOptions`, Unix-like open mode constants, async and sync wrappers for metadata/access/remove/rename/read operations, cross-platform `same_file` comparison, and directory-aware remove helpers that compensate for platform-specific remove-file behavior.

## Important APIs, Types, And Functions
- `get_readonly_options`, `get_writeonly_options`, and `get_readwrite_options` lazily initialize shared base `tokio::fs::OpenOptions`.
- `same_file` compares metadata differently on Unix and Windows.
- `FileMode` constants `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_CREATE`, `O_TRUNC`, and `O_APPEND` mimic common POSIX flags used by local disk code.
- `open_file` maps the mode flags to Tokio open options and clones base options when create/append/truncate modifiers are needed.
- `access`, `access_std`, `lstat`, `lstat_std`, `make_dir_all`, `mkdir`, `rename`, `rename_std`, and `read_file` wrap common filesystem calls.
- `remove`, `remove_all`, `remove_std`, and `remove_all_std` delete files or directories with file-first behavior and directory fallback.

## Control Flow
`open_file` chooses a base options object by masking access mode bits. If create, append, or truncate bits are set, it clones the base options and mutates the clone before opening; otherwise it reuses the cached options directly. Because `O_RDONLY` is zero, the mode mask defaults to read-only unless write bits are set.

`remove` and `remove_all` try `remove_file` first. If the error indicates a directory (`EISDIR`, `IsADirectory`, or macOS `EPERM` for remove-file on directory), `remove` falls back to `remove_dir` and `remove_all` falls back to `remove_dir_all`. The sync `remove_std` mirrors that behavior. `remove_all_std` checks metadata first and dispatches to `remove_dir_all` or `remove_file`.

`same_file` is stricter on Unix, comparing device, inode, size, permissions, and mtime. On Windows it compares permissions, file type, and length because Unix inode/device metadata is unavailable.

## State And Persistence Behavior
The file has process-local static `OnceLock` state for reusable open options. Its operations directly mutate filesystem state through create/open/truncate/append, directory creation, rename, and delete calls. It does not perform disk-layer error conversion itself; callers such as `disk/local.rs` map raw I/O errors through `error_conv.rs`.

The `open_file` flags can truncate or append persisted object/part files, so call sites must choose mode bits carefully. Remove helpers can delete either files or directories depending on the target and function.

## Dependencies And Integration Points
`disk/local.rs` imports this module for file opens, metadata checks, removal, renames, and reads. `disk/os.rs` provides complementary OS-specific helpers. Higher layers receive errors after `disk/local.rs` maps these raw I/O errors with `to_file_error`, `to_volume_error`, or `to_unformatted_disk_error`.

The module depends on Tokio filesystem APIs, standard filesystem metadata, `OnceLock`, `Arc`, and `libc` constants for directory-error detection.

## Risks And Edge Cases
- `O_RDONLY` is zero, so invalid or missing access bits silently select read-only behavior.
- `open_file` does not expose create-new/exclusive or sync flags, even though commented constants suggest POSIX parity was considered.
- Reusing cached `OpenOptions` is efficient, but callers must not mutate the cached base options. The functions return private references only, keeping that contained.
- `remove_all_std` calls `metadata` first, so a missing path returns an error before any remove attempt; async `remove_all` directly attempts removal and can return the original remove error.
- Unix `same_file` compares mtime and permissions in addition to inode/device, so the same inode after metadata changes may be considered different.

## Test Signals
Tests cover constants, open read-only/write-only/read-write/append/truncate modes, async and sync access, metadata calls, recursive directory creation, file and directory removal, recursive removal, sync removal, mkdir, async and sync rename, file read, missing-file read failure, and same/different file metadata comparisons.
