# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tarfs.c

This file implements a read-only tapefs backend for tar archives.

Key behavior:
- Scans 512-byte tar headers and stops on an empty name.
- Supports POSIX ustar prefix/name composition and old-style names.
- Parses mode, uid, gid, size, mtime, checksum, and link flag.
- Detects directories by link flag, mode, or trailing slash.
- Sanitizes names by stripping leading slashes, cleaning paths, and dropping leading `../`.
- Reads file payload blocks from archive offsets.

Important details:
- Symlinks and hard links are skipped as content-bearing entries.
- GNU positive binary size encoding is partially supported.
- Header checksums are validated after temporarily replacing the checksum field with spaces.
- Short reads are padded with zeros.

Filesystem relevance:
- Direct: maps tar archives into a safe read-only 9P namespace.
