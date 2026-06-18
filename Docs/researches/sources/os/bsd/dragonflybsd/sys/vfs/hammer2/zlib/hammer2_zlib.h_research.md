# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib.h

HAMMER2-local zlib 1.2.8 public interface header, trimmed for in-kernel compression/decompression use.

Key responsibilities:
- Defines zlib version constants, stream type `z_stream`, flush constants, status/error codes, compression levels, strategies, data-type values, and the `Z_DEFLATED` method.
- Declares deflate init, deflate, deflate end, inflate init, inflate, inflate end, and Adler-32 checksum APIs.
- Declares internal version-checking init entry points `deflateInit_()` and `inflateInit_()`.
- Defines convenience macros for `deflateInit`, `inflateInit`, `deflateInit2`, and `inflateInit2` that pass `ZLIB_VERSION` and `sizeof(z_stream)`.
- Includes HAMMER2’s zconf wrapper `hammer2_zlib_zconf.h`.

Important implementation details:
- The visible `z_stream` omits allocator callbacks compared with full upstream zlib in this copy; comments still describe allocator fields from upstream documentation.
- Comments preserve upstream zlib API semantics for streaming compression/decompression, flush modes, return codes, checksum behavior, and gzip/zlib format handling.
- `struct internal_state` is opaque to applications unless a dummy declaration is needed for compiler compatibility.
- The header is not a full general-purpose userland zlib surface; it exposes the subset needed by the bundled HAMMER2 zlib implementation.

Dependencies:
- Depends on `hammer2_zlib_zconf.h` for base zlib typedefs and configuration macros.
- Implemented by HAMMER2-local zlib source files such as deflate, inflate, trees, inffast, inftrees, zutil, and adler32 sources.

Notable risks:
- Upstream comments and local structure definitions diverge in places, especially allocator callback discussion; developers should trust the actual type definition.
- Version/init macros must match implementation `ZLIB_VERSION` and stream layout or init returns `Z_VERSION_ERROR`.
- Since this is vendored zlib 1.2.8, security or correctness updates from newer zlib versions are not automatically present.
