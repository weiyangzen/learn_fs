# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/zipfs.c

This file implements a read-only tapefs backend for ZIP archives.

Key behavior:
- Initializes flate support and opens the ZIP with `Biobuf`.
- Finds the central directory from the end-of-central-directory record.
- Reads central directory headers, converts metadata into `Fileinf`, and populates the tapefs tree.
- Supports stored files and deflated files.
- Reads local headers on demand and inflates compressed data into a per-file cache.

Important details:
- Filenames are forced to lower case.
- Text files can be marked by setting a high bit in the stored address; CRLF pairs may be munged by replacing `\r` with space.
- Deflated file cache is keyed by qid path and CRC-checked after inflate.
- Directory entries are inferred from zero-size stored names ending in `/`.
- Unsupported compression methods call `sysfatal`.

Filesystem relevance:
- Direct: exposes ZIP archives as read-only Plan 9 filesystem trees through tapefs.
