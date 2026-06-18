# File Research: sources/os/linux/linux/fs/nfsd/debugfs.c

Implements NFSD debugfs controls for server I/O behavior.

Key behavior:
- Creates `/sys/kernel/debug/nfsd`.
- Exposes `disable-splice-read`:
  - `0` allows page-splicing reads.
  - `1` forces READ to use only iov-iter reads.
  - Re-enabling splice read forces read I/O mode back to buffered.
- Exposes `io_cache_read`:
  - buffered I/O
  - buffered dropbehind/dontcache
  - direct I/O
  - dontcache/direct settings force splice-read disabled.
- Exposes `io_cache_write`:
  - buffered I/O
  - dontcache/dropbehind
  - direct I/O
- Optionally exposes `delegated_timestamps` when NFSDv4 is enabled.
- `nfsd_debugfs_init()` creates the directory and files.
- `nfsd_debugfs_exit()` removes the tree recursively and clears the top-level pointer.

Important interactions:
- Controls global NFSD read/write I/O policy variables used by server VFS I/O paths.
- Debugfs settings take effect immediately across NFS versions, exports, and NFSD network namespaces.
