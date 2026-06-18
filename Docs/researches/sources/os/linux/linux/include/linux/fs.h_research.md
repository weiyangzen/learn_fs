# File Research: sources/os/linux/linux/include/linux/fs.h

## Purpose
Central Linux VFS header defining core filesystem, inode, file, address-space, I/O, permission, timestamp, mount, and generic helper interfaces used across the kernel.

## Main Contents
- Access and open-mode flags: `MAY_*`, `FMODE_*`, `ATTR_*`, inode `S_*` flags, filesystem `FS_*` flags, `IOCB_*` flags, remap/copy flags.
- Core structures:
  - `struct iattr`: VFS attribute changes, including idmapped-mount-aware uid/gid aliases.
  - `struct kiocb`: kernel I/O control block for sync/async reads and writes.
  - `struct address_space_operations` and `struct address_space`: page-cache and mapping operations/state.
  - `struct inode`: core inode object with operation pointers, timestamps, writeback state, locks, reference counts, file ops, fsnotify state, and private data.
  - `struct file`: open-file object with mode/ops/mapping/path/position/readahead/reference state.
  - `struct file_operations` and `struct inode_operations`: primary VFS operation tables.
  - `struct file_system_type`: filesystem driver registration contract.
  - `struct filename`, `struct delayed_filename`, `struct offset_ctx`, `struct renamedata`, `struct dir_context`.
- Inline helpers for inode locking, mapping locks, `i_size` access, uid/gid idmap translation, timestamp get/set, dirty marking, link count updates, file reference access, DAX checks, write-freeze accounting, write-access denial, directory emit helpers, and `kiocb` flag setup.
- VFS API declarations for create/link/unlink/rename/mkdir/mknod/symlink, open/close, stat/statfs, truncate/fallocate, read/write/copy/remap, fsync, direct I/O, inode lookup/allocation/eviction, generic file helpers, simple filesystem helpers, casefolding, xattr/security-related setattr preparation, fadvise, and char-device registration.

## Important Design Points
- This header is a major kernel-wide contract. Changes to structures or operation tables affect filesystems, drivers, memory management, io_uring, security, fsnotify, block code, and proc/debug paths.
- `struct inode` and `struct file` are arranged for hot-path access and use `__randomize_layout`; comments document locking and lifetime expectations.
- `i_size_read()` / `i_size_write()` have architecture-specific ordering and seqcount behavior for 32-bit SMP/preemptible kernels.
- Idmapped mount helpers (`i_uid_into_vfsuid()`, `i_uid_update()`, `inode_fsuid_set()`, etc.) are embedded in the generic VFS contract.
- `file_operations` includes modern hooks for io_uring commands, iopoll, async buffered I/O capability flags, copy/remap, and the newer `mmap_prepare` compatibility path.
- `kiocb_set_rw_flags()` validates `RWF_*` against file capabilities such as `FMODE_NOWAIT`, `FMODE_CAN_ATOMIC_WRITE`, `FOP_DONTCACHE`, append restrictions, and DAX exclusions.

## Cross-File Relationships
- `include/linux/namei.h` builds on types and helpers from this file for path lookup and directory operation lifetimes.
- io_uring files in this group use `struct file`, `struct inode`, `struct file_operations`, `vfs_fadvise()`, delayed filenames, eventfd/proc callbacks, and `io_uring_cmd` hooks rooted here.
- Almost every Linux filesystem implementation depends on the operation tables, inode/file layout, and generic helpers declared here.

## Risks / Review Notes
- Structure layout changes are high risk because many subsystems depend on exact fields, locking, and lifetime rules.
- Helper semantics often encode subtle locking requirements, especially inode state, `i_rwsem` subclasses, mapping invalidation locks, direct I/O counters, and superblock freeze write accounting.
- `file_dentry()` intentionally warns if `f_path.dentry` and `f_inode` disagree, reflecting overlayfs/backing-file historical pitfalls.
- `mmap` and `mmap_prepare` hooks are mutually exclusive; `can_mmap_file()` warns and rejects invalid dual-hook configuration.
