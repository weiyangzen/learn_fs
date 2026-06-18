# File Research: sources/os/linux/linux/fs/erofs/ishare.c

Implements experimental EROFS page-cache sharing among files with identical content fingerprints.

Key behavior:
- Uses an anonymous EROFS mount to host shared inodes.
- Builds a fingerprint from inode xattrs plus domain id and hashes it with xxhash.
- `erofs_ishare_fill_inode()` finds or creates a shared inode keyed by fingerprint, verifies matching aops and size, and links the real inode into the shared inode’s list.
- `erofs_ishare_free_inode()` unlinks the real inode and drops the shared inode reference.
- Open creates a backing file pointing at the shared inode mapping and rejects `O_DIRECT`.
- Read iter clones the kiocb onto the backing file and reads from the shared page cache.
- mmap swaps the VMA file to the backing file after security checks.
- fadvise forwards to the backing file.
- `erofs_real_inode()` resolves a shared anonymous inode back to one linked real inode for mapping decisions.
- Init mounts the anonymous filesystem and sets up backing-device info; exit unmounts it.

Important interactions:
- Requires `CONFIG_EROFS_FS_PAGE_CACHE_SHARE`.
- Depends on xattr fingerprinting from `xattr.c`.
- Excluded with fscache-on-demand by Kconfig.
