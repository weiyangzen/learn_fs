# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_vfsops.c

Implements DragonFlyBSD ext2/ext3/ext4-compatible VFS operations: mount, unmount, root lookup, statfs/statvfs, sync, NFS file handles, inode-to-vnode loading, and filesystem module init/uninit. It registers `ext2fs_vfsops` via `VFS_SET(ext2fs_vfsops, ext2fs, VFCF_MPSAFE)`.

Key entry points are `ext2_mount`, `ext2_mountfs`, `ext2_unmount`, `ext2_reload`, `ext2_vget`, `ext2_sync`, `ext2_root`, `ext2_statfs`, and `ext2_statvfs`. The mount path copies `struct ext2_args`, resolves the block device with namecache lookup, enforces access checks, handles read-only/read-write transitions, export updates, clean-state validation, and calls `ext2_mountfs` for fresh mounts.

`ext2_check_sb_compat` validates the magic number and rejects unsupported incompatible or read-write-unsafe ro-compatible feature bits using the feature tables from `ext2fs.h`. Supported feature handling includes extents, 64-bit descriptors, flex_bg/meta_bg, directory indexes, checksums, large files, and extra inode size, but journaling recovery and many newer ext4 features remain unsupported.

`ext2_compute_sb_data` is the main superblock normalizer. It derives block size, fragment size, group counts, inode size, descriptor sizing, block/inode counts, max file size, checksum seed, hash signedness, and allocates/loads group descriptors. It performs many defensive checks: bad block size, unsupported fragment mismatch, invalid first inode, invalid inode size, bad group sizes, excessive descriptor count, invalid free counts, invalid first data block, inconsistent GDT checksum modes, and group descriptor placement validation.

Group descriptor support is handled through `ext2_cg_location`, `ext2_cg_validate`, `ext2_sbupdate`, and `ext2_cgupdate`. The code supports classic and 64-bit ext4 descriptor layouts, meta block groups, sparse superblocks, group descriptor checksums, and metadata checksums.

`ext2_reload` supports reloading incore data after fsck on a read-only root filesystem. It invalidates cached device metadata, rereads the superblock, recomputes mount data, resets cluster summaries, and rescans active vnodes to reload inode contents.

`ext2_mountfs` opens the device, reads and validates the superblock, refuses dirty read-write mounts unless forced, allocates `struct ext2mount`, `struct m_ext2fs`, and superblock/group data, initializes cluster summaries, marks writable filesystems dirty, sets mount flags, and installs normal/spec/fifo vnode op tables.

`ext2_vget` resolves an inode number to an incore vnode. It checks the inode hash, serializes new vnode allocation with `ext2fs_inode_hash_lock`, reads the dinode block, converts the on-disk inode via `ext2_ei2i`, zeroes unused direct blocks for non-extent regular files/directories, initializes vnode type through `ext2_vinit`, assigns generation numbers, and returns a locked vnode.

NFS export support is implemented with `ext2_fhtovp`, `ext2_vptofh`, and `ext2_check_export`, using `struct ufid` with inode number and generation. Stale handle checks reject invalid inode numbers, zero-mode inodes, generation mismatches, and unlinked inodes.

Important dependencies: `fs.h` for block/inode mapping macros, `ext2fs.h` for superblock/features, `inode.h` for incore inode layout, `ext2_mount.h`, `ext2_dinode.h`, `ext2_extents.h`, and functions declared in `ext2_extern.h` such as checksum and inode conversion helpers.

Notable risks or research hooks: mount failure cleanup only frees selected allocations; cluster summary allocations are freed on unmount but partial mount failures need careful audit. Writable mount clean-state transitions depend on `e2fs_wasvalid` and force semantics. `ext2fs_inode_hash_lock` is a simple sleep lock and is central to duplicate vnode prevention.
