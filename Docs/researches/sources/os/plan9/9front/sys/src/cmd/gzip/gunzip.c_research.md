# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gunzip.c

Implements Plan 9 `gunzip`.

Key points:
- Parses options:
  - `-c` write decompressed output to stdout
  - `-t` list/test table mode
  - `-T` set output modification times from gzip metadata
  - `-v` verbose
  - `-D` debug
- Uses Plan 9 `<flate.h>` `inflateinit()` and `inflate()`.
- Validates gzip magic bytes and compression method before processing file inputs.
- Generates output names by removing `.gz`, mapping `.tgz` to `.tar`, or refusing to overwrite unchanged names.
- Supports concatenated gzip members by repeatedly reading headers, inflating, checking trailers, and continuing until EOF.
- Parses gzip header fields including optional extra data, original filename, comment, and header CRC.
- Maintains CRC and uncompressed length through `crcwrite()`, using `mkcrctab(GZCRCPOLY)` and `blockcrc`.
- Validates trailer CRC and output length.
- Uses `setjmp`/`longjmp` to abort a bad member and remove partially written output files.
- In table mode, prints embedded names and optional size/time information without writing output.

Dependencies and interactions:
- Includes `gzip.h` for gzip constants.
- Uses Plan 9 `Biobuf`, file descriptors, `Dir`, and `<flate.h>` callbacks.
- Shares gzip format constants with `gzip.c`.

Research relevance:
- Native Plan 9 gzip decompressor wrapper around the system flate library, with filesystem-safe output handling and trailer integrity checks.
