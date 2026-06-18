# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zlib.h

Public zlib 1.2.2 API header bundled under Ghostscript’s local `zlib` directory.

- Defines `z_stream`, allocator callback types, public constants, flush modes, compression levels, strategy values, return codes, and method IDs.
- Declares core stream APIs: `deflate`, `inflate`, `deflateEnd`, `inflateEnd`, plus macro-wrapped `deflateInit`, `inflateInit`, `deflateInit2`, `inflateInit2`, and `inflateBackInit`.
- Declares advanced APIs for dictionaries, stream copy/reset, parameter changes, bounds, raw/gzip wrappers, `inflateBack`, and compile flags.
- Declares convenience APIs: `compress`, `compress2`, `compressBound`, `uncompress`.
- Declares gzip file APIs: `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzseek`, `gzclose`, `gzerror`, and related helpers.
- Declares checksum APIs `adler32`, `crc32`, `get_crc_table`, plus `zError` and `inflateSyncPoint`.

Dependencies are `zconf.h` and zlib implementation internals. This file is a vendored upstream interface, not Plan 9-specific logic. Comments document API contracts extensively, including buffer ownership, return-code semantics, gzip/zlib/raw wrapper behavior, and memory-allocation requirements.

Notable concerns: this is old zlib 1.2.2-era API text. Consumers must compile against matching implementation objects because init macros pass `ZLIB_VERSION` and `sizeof(z_stream)` for compatibility checks.
