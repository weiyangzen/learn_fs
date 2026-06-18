# File Research: sources/os/plan9/9front/sys/src/cmd/gzip/unzip.c

Implements Plan 9 `unzip`.

Key points:
- Parses options:
  - `-a` automatically create missing parent directories
  - `-c` write file contents to stdout
  - `-i` lower-case extracted/listed names
  - `-s` stream mode using local file headers instead of central directory seeks
  - `-t` table/list mode
  - `-T` set extracted modification times
  - `-v` verbose
  - `-D` debug
  - `-f zipfile` select archive file, otherwise stdin
- Supports both central directory mode and streaming local-header mode.
- `findCDir()` searches backwards for the end-of-central-directory record, reads entry counts and central-directory offset, then seeks to the directory.
- `cheader()` parses central directory entries; `header()` parses local file headers.
- `unzipEntry()` extracts one entry, creating directories or files, honoring stdout, optional auto-parent creation, and DOS directory attributes.
- Supports stored method `0` and deflate method `8`; rejects unsupported compression methods.
- Uses Plan 9 `inflate()` for deflated entries and direct copy for stored entries.
- Validates CRC, uncompressed size, and compressed size.
- Handles data-descriptor trailers when `ZTrailInfo` is set, including Apple-style optional signature `0x08074b50`.
- `wantFile()` supports exact requested files and requested directory prefixes.
- Uses `setjmp`/`longjmp` for per-entry error handling and a separate jump path to retry non-seekable input in stream mode.

Dependencies and interactions:
- Includes `zip.h`.
- Uses Plan 9 `Biobuf`, `<flate.h>`, directories, and file descriptors.
- Shares CRC polynomial and ZIP constants with `zip.c`.

Research relevance:
- Full native ZIP extractor/listing tool with both seekable and streaming archive handling, important for Plan 9 archive/file workflow.
