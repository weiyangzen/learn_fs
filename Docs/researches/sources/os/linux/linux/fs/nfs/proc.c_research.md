# File Research: sources/os/linux/linux/fs/nfs/proc.c

Implements the NFSv2 client RPC operation table and the version-specific procedure wrappers used by generic NFS client code.

Key behavior:
- Provides NFSv2 implementations for root probing, getattr, setattr, lookup, readlink, create, remove, rename, link, symlink, mkdir, rmdir, readdir, mknod, statfs, fsinfo, pathconf, read, write, and lock handling.
- `nfs_proc_get_root()` probes the root file handle with GETATTR and STATFS, retrying with the default client credential when needed, then fills NFSv2 transfer-size and filesystem limits.
- Directory mutations mark parent directories for revalidation after successful or attempted RPCs.
- NFSv2-specific quirks are handled locally:
  - `mknod` is encoded through CREATE.
  - FIFO creation retries with the original mode if the character-device workaround fails.
  - SYMLINK has no returned attributes, so instantiation falls back to LOOKUP.
  - COMMIT setup paths are `BUG()` because NFSv2 writes are always file-sync.
- Read completion refreshes inode attributes and synthesizes EOF detection from count and returned file size.
- Write setup forces `NFS_FILE_SYNC`; write completion treats the requested byte count as written and updates inode writeback attributes.
- Locking delegates to lockd via `nlmclnt_proc()` and validates 32-bit NFSv2 lock ranges.

Important interactions:
- Exports `nfs_v2_clientops`, the main NFSv2 dispatch contract consumed by generic mount, inode, page I/O, and VFS paths.
- Uses shared helpers from `internal.h`, including cache invalidation, instantiation, writeback, delegation stubs, and server/client allocation.
- The inode operation tables wire generic NFS VFS entry points to NFSv2 protocol procedures.
