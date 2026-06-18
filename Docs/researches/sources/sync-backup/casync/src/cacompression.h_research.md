# sources/sync-backup/casync/src/cacompression.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.h -->
## sources/sync-backup/casync/src/cacompression.h

Purpose: `cacompression.h` defines the compression type enum and conversion API used across casync chunk storage and user-facing options.

Important APIs and types: `CaCompressionType` enumerates XZ, gzip, and zstd, plus `_CA_COMPRESSION_TYPE_MAX` and `_CA_COMPRESSION_TYPE_INVALID`. `CA_COMPRESSION_DEFAULT` is selected at compile time: zstd if available, else gzip, else xz, else invalid. Public functions convert to/from strings.

Control flow contract: callers should validate values against `_CA_COMPRESSION_TYPE_MAX` and handle `_CA_COMPRESSION_TYPE_INVALID`, especially when no compression library is enabled. `CA_COMPRESSION_DEFAULT` is not a distinct runtime value; it aliases one concrete enum or invalid through preprocessor selection.

State and persistence: no state. The enum may be serialized indirectly through strings or chunk suffix behavior.

Dependencies and integration points: relies on build-generated macros `HAVE_LIBZSTD`, `HAVE_LIBZ`, and `HAVE_LIBLZMA`, supplied by `config.h` included globally from Meson. Used by `cachunk.h/c`, compressor code, and option parsing.

Risks: including this header without generated config macros would break default selection, but the build injects `-include config.h`. Default compression can change when build dependencies change, which affects output compatibility/performance expectations.

Test signals: build matrix tests with different compression libraries should verify default selection and conversion behavior. Runtime tests should ensure unsupported algorithms are rejected by the compressor layer even if string parsing recognizes them.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.h -->
