# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_snap.c

## Overview
`ufs_snap.c` implements UFS snapshot create/delete entry points around the generic `fssnap` copy-on-write facility. It validates privilege and filesystem state, pins backing-file vnodes, write-locks the filesystem while snapshot state is established, and seeds the snapshot candidate map from UFS allocation bitmaps.

## Main Responsibilities
- Create snapshots with `ufs_snap_create()`.
- Delete snapshots with `ufs_snap_delete()`.
- Convert user-provided backing file descriptors into held vnode arrays.
- Reject backing files located on the same filesystem being snapshotted.
- Establish a `LOCKFS_WLOCK` during snapshot setup.
- Compute chunk geometry and initialize fssnap metadata.
- Scan cylinder groups to mark chunks containing allocated fragments as copy-on-write candidates.

## Key Control Flow
- `ufs_snap_create()` requires `secpolicy_fs_config()`, rejects read-only filesystems, initializes backing vnodes, verifies the filesystem is unlocked, and write-locks it.
- Snapshot creation only proceeds when `fs_clean` is one of the active/stable/clean/logged states accepted by the code.
- Only one snapshot is allowed per `ufsvfs`; existing `vfs_snapshot` causes `EBUSY`.
- The snapshot chunk size is caller-provided or defaults to `fs_bsize * 4`; it must be at least one fragment and a multiple of fragment size.
- `fssnap_create()` allocates generic snapshot state, then `ufs_snap_find_candidates()` marks chunks containing allocated fragments.
- `fssnap_create_done()` returns the snapshot number, and success stores the snapshot handle in `ufsvfsp->vfs_snapshot`.
- All exits attempt to unlock the filesystem; errors after `fssnap_create()` delete the snapshot state.

## Backing File Handling
- `ufs_snap_init_backfile()` uses `getf()`/`releasef()` to resolve descriptors, holds each backing vnode with `VN_HOLD()`, and returns a NULL-terminated vnode array.
- `release_backing_vnodes()` releases held vnodes and frees the array.
- Backing files on the same mounted UFS instance are rejected to avoid recursive snapshot storage.

## Candidate Bitmap Scan
- `ufs_snap_find_candidates()` reads each cylinder group with `BREAD()`.
- It validates `CG_MAGIC`.
- It reads `cg_blksfree()`; in UFS, allocated fragments are represented by cleared bits.
- For each allocated fragment, it computes the snapshot chunk number and calls `fssnap_set_candidate()`, then skips to the next chunk.

## Error Handling
- User-visible `fiosnapp->error` values distinguish backing-file, lock, cleanliness, busy, chunk-size, create, bitmap, and unlock failures.
- Read-only filesystems return `EROFS`; missing snapshots on delete return `ENOENT`.
- Delete requires privilege and a read-write filesystem before calling `fssnap_delete()`.

## Research Notes
The important behavior is the atomic snapshot establishment under `LOCKFS_WLOCK` and the candidate-map seeding from allocated-fragment state. The file relies on generic fssnap strategy support and stores only one active snapshot handle in `ufsvfs`.
