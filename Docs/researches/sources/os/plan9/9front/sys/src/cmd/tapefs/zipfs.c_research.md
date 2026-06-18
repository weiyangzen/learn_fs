# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/zipfs.c

`zipfs.c` is a read-only `tapefs` backend for ZIP archives.

Population:
- Initializes CRC table and flate support.
- Opens archive with `Biobuf`.
- `findCDir` scans backward up to 1024 bytes for end-central-directory, then seeks to the central directory.
- `cheader` reads each central directory entry into `ZipHead`.
- `populate` converts central entries into `Fileinf`, deriving directories from zero-size stored entries ending in `/`, lowercasing names, setting readonly mode from DOS attributes, and converting MS-DOS timestamps.

Reads:
- `doread` seeks to the local header offset, reads local `header`, then:
  - method 0: seeks into stored data and reads directly.
  - method 8: inflates the whole file into a cached buffer when qid changes, checks CRC, optionally munges CRLF text, then copies the requested slice.
- `High64` bit in `addr` marks text-file handling.
- `blwrite` is the flate output callback into a bounded block.

Limitations/risks:
- Unsupported methods fatal.
- No ZIP64, encryption, multi-disk, or large comment search beyond 1024 bytes.
- Deflated file cache is one-file-at-a-time and static.
- `trailer` is defined but unused in normal central-directory-driven reads.
