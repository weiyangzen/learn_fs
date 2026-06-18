# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c

This file implements ext2fs VFS operations, module registration, mount/unmount/update/reload, superblock and group descriptor handling, vnode loading/creation, file-handle conversion, sync, and statvfs.

Key responsibilities:
- Register ext2fs as a NetBSD VFS module.
- Define ext2fs VFS operation table and vnode operation vector descriptors.
- Initialize/destroy ext2fs inode pool and shared UFS support.
- Mount root and non-root ext2fs filesystems.
- Validate and populate in-memory ext2 superblock data.
- Load group descriptors with support for varying descriptor sizes.
- Load existing inodes and create new vnodes/inodes.
- Update superblock and group descriptors.
- Report filesystem statistics and sync dirty vnodes/control data.
- Convert between NFS file handles and vnodes.

Important functions and structures:
- `ext2fs_vfsops`: Main VFS dispatch table. Uses ext2fs-specific mount, unmount, statvfs, sync, vget/load/newvnode, file-handle, init/done, and mountroot hooks; delegates root, quotas, start, suspend, and rename locks to shared UFS/genfs helpers.
- `ext2fs_genfsops`: Defines genfs page-cache behavior with `ext2fs_gop_alloc`.
- `ext2fs_ufsops`: Supplies ext2fs implementations for inode times, update, buffer read, and buffer write.
- `e2fs_cgload` and `e2fs_cgsave`: Convert group descriptor blocks between on-disk descriptor sizes and in-memory `struct ext2_gd` arrays.
- `ext2fs_set_inode_guid`: Reconstructs full uid/gid from low/high ext2 inode fields for revision > 0.
- `ext2fs_init`, `ext2fs_reinit`, `ext2fs_done`: Manage the ext2 inode pool and shared UFS lifecycle.
- `ext2fs_mountroot`: Mounts root from `root_device`, initializes mount info, statvfs, and root filesystem time.
- `ext2fs_mount`: Handles new mounts, getargs, update mounts, read-write/read-only transitions, reloads, device authorization/opening, mount info, and clean/dirty superblock state.
- `ext2fs_loadvnode_content`: Reads an ext2 dinode from a buffer, validates `extra_isize`, allocates dinode storage, byteswaps/loads it, and sets uid/gid.
- `ext2fs_reload`: For read-only mounted filesystems, invalidates device metadata, rereads superblock and group descriptors, invalidates vnode buffers, and reloads active inode contents.
- `ext2fs_mountfs`: Common mount logic. It flushes old device buffers, reads and validates superblock, allocates `m_ext2fs` and `ufsmount`, loads group descriptors, verifies/initializes cylinder groups, sets mount flags, block shifts, dir block size, symlink length, and max file size.
- `ext2fs_unmount`: Flushes files, marks clean when possible, updates control data, closes device, frees group descriptors and mount structures.
- `ext2fs_statvfs`: Computes filesystem overhead from bitmaps, inode tables, superblock/group descriptor copies, sparse-super variants, and resize-reserved descriptors; fills block/inode availability.
- `ext2fs_sync`: Iterates dirty/modified vnodes, fsyncs or updates them, syncs device vnode, and writes modified control data.
- `ext2fs_init_vnode`, `ext2fs_loadvnode`, `ext2fs_newvnode`: Allocate/load inode structures, initialize vnodes/genfs nodes, assign generation numbers, set new inode ownership/mode/link count, initialize extra inode size and creation time.
- `ext2fs_fhtovp` and `ext2fs_vptofh`: Validate ext2 inode number/generation and convert to/from `struct ufid`.
- `ext2fs_sbupdate` and `ext2fs_cgupdate`: Write superblock and group descriptors.
- `ext2fs_sbfill`: Validates ext2 magic, revision, block size, group counts, inode size, descriptor size, unsupported incompat/rocompat features, and computes in-memory block geometry.

Important interactions:
- Owns mount-time setup consumed by every ext2fs vnode operation.
- Uses shared UFS `vcache`, quota, root, close, reclaim, and vget infrastructure.
- Superblock feature checks gate whether the filesystem can be mounted read-write.
- `ext2fs_mountfs` sets `IMNT_DTYPE | IMNT_SHRLOOKUP`, `um_maxsymlinklen`, and `um_dirblksiz`, which affect lookup, directory operations, and symlink handling.

Notable behavior and risks:
- Read-write mounts mark clean filesystems dirty and mark unclean filesystems with `E2FS_ERRORS`.
- On read-only transition, it flushes files and marks the filesystem clean only if control data update succeeds and no error state is set.
- `ext2fs_sbfill` supports ext2/ext3/ext4-style fields selectively, including 64-bit group descriptor sizing, but rejects unsupported incompat features unless compile-time ignore macros are set.
- `ext2fs_newvnode` sets `e2di_extra_isize` from `e4fs_want_extra_isize` when the feature and inode size allow it.
