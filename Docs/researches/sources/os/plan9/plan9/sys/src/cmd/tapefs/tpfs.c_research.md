# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tpfs.c

This file implements a tapefs backend for old `tp` tape images.

Key behavior:
- Reads a directory table sized for magtape while tolerating dectape by checksum filtering.
- Validates per-entry checksum.
- Extracts file block address, 24-bit size, timestamp, mode, uid, gid, and name.
- Inserts entries into the tapefs tree and reads data from 512-byte block addresses.

Important details:
- Reports counts of bad and good checksums.
- Absolute paths are made relative.
- Write/create/truncate operations are disabled.

Filesystem relevance:
- Direct: exposes historical `tp` tape contents as a read-only mounted filesystem.
