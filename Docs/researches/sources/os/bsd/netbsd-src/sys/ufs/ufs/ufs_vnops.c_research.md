# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vnops.c

This file implements the generic UFS vnode operations for metadata, namespace mutations, directories, symlinks, special/fifo wrappers, vnode initialization, allocation, and buffer-I/O helpers.

Key responsibilities:
- Create, mknod, remove, link, mkdir, rmdir, symlink, readlink, whiteout, and readdir operations.
- Implement access checks, getattr, setattr, chmod, and chown.
- Integrate quota accounting, ACL checks/inheritance, WAPBL updates, and namecache updates.
- Initialize special/fifo vnode operations and device aliases.
- Provide UBC allocation and buffer-I/O wrappers used by other UFS code.

Important functions:
- `ufs_create` / `ufs_mknod`: Use lookup results in `i_crap`, call `ufs_makeinode`, end the WAPBL transaction, and unlock new vnodes.
- `ufs_open` / `ufs_close`: Enforce append-only open semantics and update times on close.
- `ufs_accessx`: Combines readonly/snapshot/immutable/quota checks with POSIX.1e, NFSv4 ACL, or Unix permission checks.
- `ufs_getattr`: Flushes pending times and exports UFS1/UFS2 inode attributes, timestamps, flags, bytes, type, and filerev.
- `ufs_setattr`: Handles flags, ownership, size, timestamps, birthtime, and mode updates with WAPBL, authorization, truncation, and cache identity refresh.
- `ufs_chmod` / `ufs_chown`: Apply authorization, ACL synchronization, quota transfer, mode/owner updates, and cache identity updates.
- `ufs_remove`: Removes non-directory entries using lookup results and `ufs_dirremove`.
- `ufs_link`: Increments link count, writes inode, inserts new directory entry, and rolls back on insertion failure.
- `ufs_whiteout`: Creates or deletes directory whiteout entries for supported directory formats.
- ACL inheritance helpers: Apply POSIX.1e or NFSv4 inherited ACLs to new directories/files.
- `ufs_mkdir`: Allocates a directory inode, initializes `.` and `..`, updates parent link count, writes directory contents, and enters the parent entry.
- `ufs_rmdir`: Verifies emptiness, removes the parent entry, updates link counts, truncates the removed directory, and purges caches.
- `ufs_symlink` / `ufs_readlink`: Store/read short symlinks inline and long symlinks via buffer I/O, preserving historical off-by-one compatibility.
- `ufs_readdir`: Converts on-disk `struct direct` entries to user `struct dirent`, handles byte swapping, produces cookies, and advances offsets by physical directory positions.
- `ufs_strategy`: Maps logical to physical blocks, calls device strategy, and applies WAPBL replay reads when needed.
- `ufs_vinit`: Assigns vnode type, special/fifo ops, root flag, device numbers, and modrev.
- `ufs_makeinode`: Shared file creation helper that allocates an inode, writes it before the directory entry, applies ACL inheritance, inserts the directory entry, and enters namecache.
- `ufs_gop_alloc`, `ufs_gop_markupdate`, `ufs_bufio`: Page-cache allocation, update marking, and typed buffer read/write wrapper.

Important interactions:
- Depends on lookup results from `ufs_lookup.c`.
- Calls quota functions through `chkdq`/`chkiq`.
- Calls filesystem-specific operations through `UFS_*` macros from `ufsmount.h`.
- Uses WAPBL around metadata and directory operations.
- Integrates with specfs, fifofs, genfs, UBC/UVM, ACL helpers, and optional dirhash.

Notable behavior and risks:
- Many namespace operations rely on `i_crap` lookup results remaining valid while the directory remains locked.
- `ufs_readdir` intentionally reads whole directory blocks and may rescan entries on later calls because `dirent` records can be larger than on-disk directs.
- Short symlink comparison uses historical `< um_maxsymlinklen` behavior, intentionally preserving existing filesystem image compatibility.
