# File Research: sources/os/linux/linux-stable/fs/nfsd/debugfs.c

Purpose: Provides debugfs controls for global NFSD I/O behavior.

Key responsibilities:
- Creates `/sys/kernel/debug/nfsd`.
- Exposes `disable-splice-read`:
  - `0` allows page splicing for NFS READ,
  - `1` forces iov-iter read.
- Exposes `io_cache_read`:
  - buffered,
  - dontcache/dropbehind,
  - direct I/O.
- Exposes `io_cache_write`:
  - buffered,
  - dontcache/dropbehind,
  - direct I/O accepted by setter.
- Ensures enabling dontcache/direct read disables splice read.
- Optionally exposes NFSv4 delegated timestamp toggle.
- Provides init/exit helpers for debugfs tree.

Integration:
- Built only with `CONFIG_DEBUG_FS`.
- Mutates global NFSD tunables consumed by server VFS I/O paths.

Risks and notes:
- Settings apply immediately across all NFS versions, exports, and NFSD net namespaces.
- Invalid cache mode values return `-EINVAL`.
