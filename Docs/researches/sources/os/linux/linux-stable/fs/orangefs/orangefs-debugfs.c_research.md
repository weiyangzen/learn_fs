# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.c

## Scope

This file implements OrangeFS debugfs support for kernel/client debug keyword help and runtime debug mask updates.

## APIs Covered

- Lifecycle: `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`, `orangefs_prepare_debugfs_help_string()`.
- Debugfs file operations for `debug-help`, `kernel-debug`, and `client-debug`.
- Keyword conversion: mask-to-string and string-to-mask helpers for kernel and client masks.
- Device ioctl receivers: `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, `orangefs_debugfs_new_debug()`.

## Control Flow And Behavior

- Module init builds a debug-help string with known kernel keywords and placeholder client text, then creates `/sys/kernel/debug/orangefs`.
- Kernel debug mask is initialized from module parameter, normalized through keyword conversion, and protected from being overwritten by a zero client-provided mask if set at module load.
- Client keyword/mask data is learned later through device ioctls; the help string and `client-debug` file are rebuilt after the first client metadata arrives.
- Writes to `kernel-debug` parse keyword lists directly into `orangefs_gossip_debug_mask`.
- Writes to `client-debug` require the daemon to be running, convert keywords to two-mask client representation, and send an OrangeFS PARAM op to userspace.
- Special keywords `all` and `verbose` are treated as aggregate masks.

## Risks And Invariants

- `orangefs_debug_lock` protects debug string file data; `orangefs_help_file_lock` protects help string reads/rebuilds.
- Client keyword arrays are dynamically allocated from newline-delimited client metadata and reused for string/mask conversion.
- User-provided debug strings are length-capped and trimmed before parsing.
- Debugfs removal is recursive and frees the help string.
