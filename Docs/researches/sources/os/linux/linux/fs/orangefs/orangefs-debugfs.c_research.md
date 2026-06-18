# File Research: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.c

Implements OrangeFS debugfs controls under `/sys/kernel/debug/orangefs`.

Key behavior:
- Creates `debug-help`, `kernel-debug`, and later `client-debug` files.
- Maintains kernel keyword-to-mask mapping from `orangefs-debug.h`.
- Initially publishes help text with unknown client keywords; after userspace client reports its keyword/mask table, rebuilds help text and creates/updates `client-debug`.
- `orangefs_debug_read/write()` reads current debug strings and writes keyword lists. Kernel writes update `orangefs_gossip_debug_mask`; client writes send an `ORANGEFS_VFS_OP_PARAM` request to userspace.
- Converts masks to comma-separated keyword strings and keyword strings back to validated masks for kernel and client masks.
- Supports client debug mask/string updates through device ioctls: `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()`.

Important synchronization:
- `orangefs_debug_lock` protects debug file backing strings.
- `orangefs_help_file_lock` protects debug-help contents.
- Module-load kernel debug mask can be preserved from being overwritten by client startup defaults.
