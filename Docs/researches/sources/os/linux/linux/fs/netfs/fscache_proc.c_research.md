# File Research: sources/os/linux/linux/fs/netfs/fscache_proc.c

Creates FS-Cache procfs visibility under the shared netfs proc tree.

Key responsibilities:
- Creates compatibility symlink `fs/fscache` pointing to `netfs`.
- Creates sequence files:
  - `fs/netfs/caches`
  - `fs/netfs/volumes`
  - `fs/netfs/cookies`
- Cleans up procfs entries.

Important APIs:
- `fscache_proc_init()`.
- `fscache_proc_cleanup()`.

Notable issue:
- Cleanup removes `fs/fscache` subtree/symlink, while creation also adds files under `fs/netfs`; the broader `netfs_exit()` removes the full `fs/netfs` subtree.
