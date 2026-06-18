# File Research: sources/os/linux/linux/fs/netfs/fscache_internal.h

Small include shim for FS-Cache-internal compilation units.

Key content:
- Includes `internal.h`.
- Overrides `pr_fmt` to prefix messages with `FS-Cache: `.

Purpose:
- Allows FS-Cache source files to share the broader netfs internal definitions while using FS-Cache-specific logging prefixes.
