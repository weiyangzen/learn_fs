# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gunzip.c

Plan 9 gzip decompressor built on the system `<flate.h>` inflate API.

- Supports `gunzip [-ctvTD] [file ...]`.
- Reads gzip headers, validates magic and deflate method, parses optional extra, original filename, comment, and header CRC fields.
- Uses `inflateinit()` once, then `inflate()` with `Bgetc` input and `crcwrite` output callback.
- Maintains CRC-32 using `mkcrctab(GZCRCPOLY)` and `blockcrc`.
- Validates trailer CRC and uncompressed length after each gzip member.
- Supports table/listing mode, stdout mode, verbose extraction, and optional restoration of modification time.

State is mostly global: input filename, output-delete path, CRC, length counters, table/verbose flags, and `jmp_buf` for error recovery.

Notable concerns:
- Output filename handling uses a fixed 256-byte buffer.
- Multiple gzip members are supported by looping until input EOF.
- Corruption after a completed gzip member is reported and ignored using `gzok`.
