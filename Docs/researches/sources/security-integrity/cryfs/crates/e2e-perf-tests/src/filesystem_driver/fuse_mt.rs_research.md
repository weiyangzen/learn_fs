# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuse_mt.rs

## Purpose
Implements `FilesystemDriver` using rustfs's object/high-level API, modeling fuse-mt-style path-based operations without a real mount.

## Important APIs, types, and functions
- `FusemtFilesystemDriver` wraps `ObjectBasedFsAdapter<Device>`.
- `NodeHandle = AbsolutePathBuf`; `FileHandle = cryfs_rustfs::FileHandle`.
- Implements all common filesystem operations: create, mkdir, symlink, attrs, chmod/chown/truncate/time updates, open/release, readdir, read/write, rename, fsync.
- `ReadCallbackImpl` captures async callback data in `Arc<Mutex<Option<FsResult<Vec<u8>>>>>`.

## Control flow
Most operations convert parent/name handles into absolute paths and call corresponding high-level rustfs methods with fixed `request_info()`. `release` simulates FUSE flush before release. `readdir` opens a directory, reads entries, releases the handle, then normalizes self/parent references. Reads use callback capture because the rustfs API returns data through a callback.

## State and persistence behavior
Driver owns an async-drop guard around the adapter/device. Reset after setup flushes adapter cache; reset after test does nothing because this object adapter has no separate cache to clear. Filesystem data persists in the fixture's tracked block/blob stores.

## Dependencies and integration points
Bridges the generic test fixture to `cryfs_rustfs::object_based_api::ObjectBasedFsAdapter`, high-level async API traits, CryFS `CryDevice`, and path types.

## Risks and edge cases
Path-based handles avoid inode cache modeling, so operation counts differ from fuser driver variants. Read callbacks unwrap captured results and will panic if the callback is not invoked.

## Test signals
All operation modules instantiated with the Fusemt fixture compare expected blobstore/high-level/low-level counts and functional success.
