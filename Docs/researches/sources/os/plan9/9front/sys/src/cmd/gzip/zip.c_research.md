# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/zip.c

Implements Plan 9 `zip`.

Key points:
- Parses options:
  - `-f zipfile` write archive to named file, otherwise stdout
  - `-v` verbose
  - `-D` debug
  - `-1` through `-9` compression level
- Recursively archives input files and directories.
- Builds an in-memory array of `ZipHead` records for later central-directory emission.
- For each file:
  - records DOS-style version fields
  - converts Plan 9 `Dir` mtime into MS-DOS time/date
  - sets DOS external attributes
  - stores local-header offset
  - compresses regular files with deflate method `8`
- Directory entries are stored with method `0` and trailing slash names.
- When writing to stdout, sets `ZTrailInfo` and writes CRC/size data after compressed data; otherwise seeks back into the local header to fill CRC and sizes.
- `putCDir()` emits all central-directory entries and the end-of-central-directory record.
- Uses `crcread()` to feed data while computing CRC and uncompressed length, and `zwrite()` to count compressed bytes.
- Aborts through `longjmp` and removes a named output archive on fatal error.

Dependencies and interactions:
- Includes `zip.h`.
- Uses Plan 9 `<flate.h>` `deflate()`.
- Paired with `unzip.c`.

Research relevance:
- Native ZIP writer covering recursive directory traversal, local headers, central directory construction, streamed archive output, and CRC/size bookkeeping.
