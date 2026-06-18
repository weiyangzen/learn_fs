# File Research: sources/os/linux/linux-stable/fs/netfs/fscache_internal.h

Tiny compatibility/internal wrapper for FS-Cache-specific formatting.

Key behavior:
- Includes the shared netfs internal header.
- Overrides `pr_fmt` to prefix messages with `FS-Cache:`.
- Contains no data structures or executable logic beyond preprocessing.
