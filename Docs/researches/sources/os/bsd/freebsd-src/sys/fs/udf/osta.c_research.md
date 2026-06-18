# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/osta.c

OSTA UDF helper routines for CS0 Unicode compression and CRC checksums.

Key responsibilities:
- Implements `udf_UncompressUnicode` for CS0 compressed names with compression IDs 8 and 16.
- Implements `udf_UncompressUnicodeByte`, preserving byte order for later iconv conversion.
- Implements `udf_CompressUnicode`.
- Defines the CRC lookup table and implements `udf_cksum` and `udf_unicode_cksum`.
- Contains optional inactive test and filename translation code behind `MAIN` and `NEEDS_ISPRINT`.

Dependencies:
- Includes `fs/udf/osta.h` for `byte`, `unicode_t`, constants, and prototypes.
- Active callers are mainly UDF vnode name translation and descriptor checksum users.

Notable risks:
- The decompression routines only validate the compression ID; callers are responsible for input sanity and output buffer capacity.
- Optional `UDFTransName` code is declared in the header but not compiled unless `NEEDS_ISPRINT` is defined.
- Non-ASCII name handling in active UDF code depends on either kernel iconv or lossy fallback behavior.
