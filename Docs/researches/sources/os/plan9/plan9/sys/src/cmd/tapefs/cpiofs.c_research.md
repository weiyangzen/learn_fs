# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/cpiofs.c

This file implements a read-only tapefs backend for old octal cpio archives.

Key behavior:
- Sequentially scans cpio headers from the archive.
- Parses octal fields for mode, uid, gid, size, mtime, and name length.
- Stops at empty names or `TRAILER!!!`.
- Adds regular files and directories into the shared `Ram` tree.
- Reads file contents from recorded archive offsets.

Important details:
- Absolute pathnames are made relative by skipping the leading slash.
- Unknown/non-regular/non-directory modes are assigned mode 0.
- Header/data offsets are advanced without explicit padding handling beyond the old format fields.

Filesystem relevance:
- Direct: maps a cpio archive into a read-only 9P namespace.
