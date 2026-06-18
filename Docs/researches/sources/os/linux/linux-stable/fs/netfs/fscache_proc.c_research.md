# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_proc.c

Creates FS-Cache procfs visibility under the netfs proc tree.

Key behavior:
- Adds `/proc/fs/fscache` as a symlink to `netfs`.
- Creates `fs/netfs/caches`, `fs/netfs/volumes`, and `fs/netfs/cookies`.
- Cleanup removes the `fs/fscache` proc subtree.
- Depends on seq operations supplied by cache, volume, and cookie files.
