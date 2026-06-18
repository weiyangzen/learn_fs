# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/device.rs

## Purpose
Defines `CryDevice`, the `cryfs_rustfs::object_based_api::Device` adapter for a CryFS filesystem backed by a `ConcurrentFsBlobStore`. It owns the root blob id, atime policy, async-drop blobstore guard, and a shared last-access timestamp used by idle unmount logic.

## Important APIs, types, and functions
- `CryDevice::load_filesystem` wraps an existing blobstore and root id; `create_new_filesystem` creates and flushes a root directory blob before exposing the device.
- `sanity_check` opens the root dir and enumerates entries to validate the loaded filesystem.
- Private path loaders `load_blob`, `load_blob_from_relative_path`, and `load_two_blobs` traverse directory entries and handle shared-prefix loading for rename.
- The `Device` impl exposes associated node/dir/file/symlink/open-file adapters, updates `last_access_time` in `on_operation`, returns `rootdir`, performs `rename`, and computes `statfs`.
- `check_entry_overwrite_allowed` enforces file/dir overwrite compatibility and rejects overwriting non-empty directories.

## Control flow
Root access constructs a root `NodeInfo` without loading the root until a directory operation needs it. Path traversal repeatedly locks the current directory blob, resolves an entry id, drops the previous blob when owned, and loads the next blob. Rename first rejects moving a path into its own descendant and root rename cases, then splits source/destination parents. Same-parent rename delegates to `DirBlob::rename_entry_by_name`; cross-parent rename loads both parents, clones the source entry, loads the child blob, removes the source entry, adds/overwrites the destination, and updates the child parent pointer.

## State and persistence behavior
Persistent state is entirely in fsblobstore blobs: directory entries, blob type, parent pointers, and block counts. `create_new_filesystem` persists the root directory. Rename mutates directory blobs and, for cross-directory moves, the child blob's parent pointer. `statfs` reads used/free block estimates from the blobstore. `last_access_time` is runtime-only atomic state for idle unmount.

## Dependencies and integration points
This file integrates `cryfs_blobstore`, `cryfs_fsblobstore`, `cryfs_blockstore::RemoveResult`, `cryfs_rustfs` device traits and error types, `AsyncDropGuard`/`AsyncDropArc`, `maybe_owned`, `AtomicInstant`, and path utilities. It is the entry point consumed by `cryfs-runner::make_device` and the RustFS/FUSE backend.

## Risks and edge cases
Cross-parent rename has explicit TODOs for race windows and exception safety: source entry removal can succeed before destination add or parent-pointer update fails. Error mapping sometimes collapses storage failures to `UnknownError` or EIO-like custom errors. Overwrite checks depend on parent entry type being honest; corrupted type/blob mismatches are surfaced as filesystem corruption only when loading the overwritten directory.

## Test signals
No local tests are in this file. Indirect signals should come from filesystem operation tests that cover root load, statfs, same-parent rename, cross-parent rename, overwrite type rules, non-empty directory overwrite rejection, and idle-unmount access timestamp updates.
