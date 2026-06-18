# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.c

Plan 9 gzip compressor built on `<flate.h>` deflate.

- Supports `gzip [-vcD] [-1-9] [file ...]`.
- Writes gzip header with magic, deflate method, optional original filename, mtime, and OS field.
- Uses `deflateinit()` and `deflate()` with `crcread` and `gzwrite` callbacks.
- Calculates CRC-32 and total uncompressed length, then writes gzip trailer.
- Converts `.tar` input suffix to `.tgz`; otherwise writes `<name>.gz`.
- Rejects directories and removes incomplete output on write/compression failure.

Dependencies are Plan 9 `libc`, `bio`, `flate`, and local `gzip.h`.

Notable concerns: archive member name is the original path string passed to `gzip()`, not just the basename in all cases. Output filename generation mutates local strings and uses fixed-size buffers.
