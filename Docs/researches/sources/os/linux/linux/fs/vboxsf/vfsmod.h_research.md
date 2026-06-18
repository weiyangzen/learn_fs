# File Research: sources/os/linux/linux/fs/vboxsf/vfsmod.h

## Purpose
Internal vboxsf header defining shared data structures, constants, operation declarations, and cross-file function prototypes.

## Main Contents
- Constants/macros:
  - `DIR_BUFFER_SIZE` set to 16 KiB.
  - `VBOXSF_SBI()` and `VBOXSF_I()` accessors.
- Mount/context state:
  - `struct vboxsf_options`: ttl, uid/gid, mode override flags, modes, masks.
  - `struct vboxsf_fs_context`: parsed options and NLS name.
  - `struct vboxsf_sbi`: per-mount state including root info, inode IDR, NLS table, root handle, bdi id, and case-insensitive flag.
- Inode/directory state:
  - `struct vboxsf_inode`: force-restat flag, handle list/mutex, embedded VFS inode.
  - `struct vboxsf_dir_info` and `struct vboxsf_dir_buf`: cached directory listing storage.
- Extern declarations for inode/file/dentry/address-space ops.
- Prototypes for file, utility, and host wrapper functions.

## Important Design Points
- `handle_list_mutex` is the synchronization point for open handles on an inode.
- `ino_idr_lock` protects synthetic inode-number allocation and removal.
- The header centralizes module-internal API boundaries without exposing them outside vboxsf.

## Cross-File Relationships
- Includes `shfl_hostintf.h`.
- Used by every vboxsf implementation file.

## Risks / Review Notes
- Changes to shared structs affect multiple implementation files and inode lifetime behavior.
- `force_restat` is an int flag, not atomic; usage depends on VFS serialization and best-effort cache coherency.
