# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/gzip.c

Implements Plan 9 `gzip`.

Key points:
- Parses options:
  - `-c` write compressed output to stdout
  - `-n` suppress stored modification time
  - `-v` verbose
  - `-D` debug
  - `-1` through `-9` compression level
- Initializes Plan 9 deflate support with `deflateinit()`.
- For file inputs, rejects directories, derives output names, and maps `.tar` to `.tgz`.
- Writes a gzip header with magic bytes, deflate method, optional filename, modification time, extra flags, and OS code.
- Uses `deflate()` with `crcread()` input and `gzwrite()` output callbacks.
- Tracks CRC and total uncompressed bytes while reading.
- Writes gzip trailer CRC and original length in little-endian order.
- On write failure, removes incomplete non-stdout output.

Dependencies and interactions:
- Includes `gzip.h` for constants.
- Uses Plan 9 `<flate.h>` rather than vendored zlib.
- Paired with `gunzip.c`.

Research relevance:
- Minimal gzip creator around Plan 9’s flate callback API and gzip wire-format framing.
