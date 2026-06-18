# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zlib.h

Defines the public zlib 1.2.2 API bundled under Ghostscript.

Key points:
- Identifies `ZLIB_VERSION` as `1.2.2` and `ZLIB_VERNUM` as `0x1220`.
- Declares the `z_stream` structure, allocator hooks, stream state pointer, byte counters, `data_type`, checksum field, and reserved field.
- Defines canonical zlib flush values, return codes, compression levels, compression strategies, data type hints, the deflate method, and `Z_NULL`.
- Documents and declares stream APIs:
  - `deflate`, `deflateEnd`, `deflateSetDictionary`, `deflateCopy`, `deflateReset`, `deflateParams`, `deflateBound`
  - `inflate`, `inflateEnd`, `inflateSetDictionary`, `inflateSync`, `inflateReset`
  - `deflateInit2_`, `inflateInit2_`, and version/structure-size checking macros
  - `inflateBack`, `inflateBackEnd`, and `inflateBackInit_`
- Declares utility APIs:
  - `compress`, `compress2`, `compressBound`, `uncompress`
  - gzip file interface: `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzputs`, `gzgets`, `gzputc`, `gzgetc`, `gzungetc`, `gzflush`, `gzseek`, `gzrewind`, `gztell`, `gzeof`, `gzclose`, `gzerror`, `gzclearerr`
  - checksums: `adler32`, `crc32`
  - introspection: `zlibVersion`, `zlibCompileFlags`, `zError`, `inflateSyncPoint`, `get_crc_table`
- The long comments are part of the API contract: caller ownership of input/output pointers, flush semantics, dictionary behavior, raw/gzip/zlib wrapper options, and expected return-code handling.

Dependencies and interactions:
- Includes `zconf.h` for portability types and export macros.
- Implemented by the rest of the bundled zlib sources under `cmd/gs/zlib`.
- Used as the external-facing compression ABI for Ghostscript’s vendored zlib copy.

Research relevance:
- This is a third-party bundled interface, not Plan 9-specific filesystem code, but it is important dependency surface for Ghostscript compression, gzip stream, checksum, and inflate/deflate behavior.
