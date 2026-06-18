# sources/object-store/rustfs/crates/ecstore/src/disk/os.rs

## Purpose
This file provides small OS/filesystem utility functions used by the disk layer. It centralizes path-length validation, root-disk detection, directory creation, directory listing, and reliable rename behavior with error conversion into the disk error model.

## Important APIs, types, and functions
`check_path_length` validates a path string against platform limits and rejects trivial dangerous Unix paths `"."`, `".."`, and `"/"`. It enforces macOS whole-path length of 1016, Windows whole-path length of 1024, and per-segment length of 255 characters on all platforms.

`is_root_disk` checks whether a disk path is the same device as the root path using `rustfs_utils::os::same_disk`; Windows always returns false.

`make_dir_all` validates path length then calls `reliable_mkdir_all`. `is_empty_dir` reads at most one entry using `read_dir`. `read_dir` returns visible file names and directory names with a trailing slash, skipping empty, `"."`, and `".."` entries and honoring a count limit where `0` means stop after the first accepted entry and negative values effectively mean unlimited in current callers.

`rename_all` wraps `reliable_rename` and converts IO errors to disk file errors. `rename_all_ignore_missing_source` uses the same inner rename but turns source `NotFound` into success, which is useful for cleanup paths.

`reliable_rename_inner` creates the destination parent if missing, retries a failed `rename_std` once, optionally logs a warning, and returns the final IO result. `reliable_mkdir_all` retries directory creation once after walking the base directory upward if the first attempt fails with `NotFound`. `os_mkdir_all` tries direct `mkdir`, creates missing parents only after direct failure, and never creates paths under `base_dir` when `base_dir` starts with the requested directory path. `file_exists` is a simple synchronous metadata probe.

## Control flow
Directory creation flows through `make_dir_all -> reliable_mkdir_all -> os_mkdir_all`. The code first validates path length, then tries to create the target. On missing parents, it creates the parent chain and retries the final mkdir. `reliable_mkdir_all` handles a first `NotFound` by adjusting the base dir to its parent once before retrying.

Rename flows through `rename_all` or `rename_all_ignore_missing_source` into `reliable_rename_inner`. Before rename, the destination parent is created if absent. The first `rename_std` failure is retried once unconditionally. On the second failure, normal `rename_all` logs and returns the error; the ignore-missing variant suppresses only `NotFound`.

Directory listing uses `tokio::fs::read_dir`, filters non-useful names, classifies entries by async `file_type`, appends a slash to directories, decrements the counter for each accepted entry, and breaks when the counter reaches zero.

## State and persistence behavior
The module does not keep in-memory state. It mutates filesystem state by creating directories and renaming files/directories. `read_dir`, `is_empty_dir`, `file_exists`, and `is_root_disk` are observational. Rename behavior depends on underlying filesystem atomicity for `rename_std`, while parent creation can introduce extra directories as a side effect.

## Dependencies and integration points
It depends on `DiskError`, disk `Result`, `to_file_error`, `rustfs_utils::path::SLASH_SEPARATOR`, `rustfs_utils::os::same_disk`, `tokio::fs`, tracing warnings, and lower-level `disk::fs` wrappers (`rename_std`, `mkdir`, `make_dir_all`). `local.rs` uses these helpers heavily for object writes, metadata writes, trash movement, startup cleanup, stale tmp cleanup, and volume creation.

## Risks and edge cases
`check_path_length` is byte/character-count based and does not canonicalize paths, so callers still need root-confinement checks. It rejects only `"."`, `".."`, and `"/"` as whole paths, not embedded traversal; `local.rs` handles that separately through normalization.

`read_dir` treats `count == 0` as "break after first accepted entry" because the counter is decremented before the equality check, while its comment says count `0` is unlimited. Current callers use `1` for emptiness and `-1` for unlimited; a future caller passing `0` could get surprising results.

`reliable_rename_inner` retries any first rename failure, regardless of kind. This can mask transient parent-creation races but also repeats permanent permission or cross-device errors. It creates destination parents before knowing whether the source exists.

`os_mkdir_all` has non-obvious `base_dir.starts_with(dir_path)` guard behavior. Callers must pass the correct base boundary to avoid skipping required creation or creating too much of the tree.

## Test signals
The tests assert that `rename_all` returns `DiskError::FileNotFound` and does not create a destination when the source is missing, while `rename_all_ignore_missing_source` returns success and also leaves the destination absent. Broader behavior is covered indirectly by `local.rs` tests that create volumes, write metadata, move temp directories, and rename/delete filesystem paths.
