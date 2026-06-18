# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/unzip.c

Plan 9 ZIP extractor/listing utility.

- Supports `unzip [-cistTvD] [-f zipfile] [file ...]`, plus `-a` auto-directory creation.
- Can read central-directory archives or streaming local-header mode with `-s`; if seeking fails it retries as stream mode.
- Parses local headers, central directory headers, end-of-central-directory records, filenames, optional trailer descriptors, and MS-DOS timestamps.
- Supports stored method `0` and deflated method `8`; other methods are rejected.
- Filters requested file names by exact path or directory prefix.
- Extracts to stdout, files, or directories, restores mtimes with `-T`, optionally lowercases names with `-i`, and validates CRC, compressed size, and uncompressed size.

Dependencies are Plan 9 `bio`, `flate`, local `zip.h`, and CRC helpers.

Notable concerns:
- `findCDir()` assumes the end-of-central-directory header is exactly at EOF minus fixed header size, so ZIP file comments are not handled.
- `mkpdirs()` contains an unconditional `print("%s\n", path);`, so `-a` auto-directory mode can emit unexpected path lines.
- Zip64, encryption, patched data, and most compression methods are unsupported.
