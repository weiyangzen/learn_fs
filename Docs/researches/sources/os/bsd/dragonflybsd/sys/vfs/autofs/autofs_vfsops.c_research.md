# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vfsops.c

## Summary
Implements autofs VFS lifecycle operations: module init/uninit, mount, unmount, root lookup, and statfs/statvfs.

## Main Responsibilities
- Initializes global autofs softc, request/node objcaches, condition variable, mutex, and `/dev/autofs` device node.
- Refuses module uninit while the control device is open and destroys device/caches/softc on unload.
- Mounts autofs by copying mount arguments, allocating `struct autofs_mount`, creating the root autofs node, assigning a fsid, and installing vnode ops.
- Handles mount updates by flushing autofs cache state.
- Unmounts by flushing vnodes, completing outstanding requests for that mount with `ENXIO`, deleting all autofs nodes, and freeing mount state.
- Returns a synthetic directory root vnode and zero-capacity statfs/statvfs values.
- Registers the filesystem as synthetic and MPSAFE.

## Important Behavior
Unmount loops until no outstanding request references the mount remain, broadcasting completion and sleeping between checks. Because autofs does not support `rmdir`, unmount force-deletes nested indirect-map nodes bottom-up after vnodes are gone.

## Risks
`autofs_uninit()` frees `autofs_softc` after dropping internal resources and comments note a race with open. Unmount safety depends on preventing new triggerings after `vflush()` and correctly completing all outstanding requests for the mount.
