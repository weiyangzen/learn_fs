# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.c

Read completely: 520 lines.

Provides OSTA-derived support routines for UDF Unicode compression, checksums, and portable filename translation. The file is shared-style code: it can be built in kernel contexts and in tool contexts with `nbtool_config.h`.

`udf_UncompressUnicode()` decodes OSTA CS0 compressed Unicode names with compression IDs 8 or 16, treating deleted-entry IDs 254 and 255 as 8-bit and 16-bit encodings. `udf_CompressUnicode()` performs the reverse compression into CS0 byte streams.

The file embeds a CRC-CCITT-style 256-entry table and exposes `udf_cksum()` for byte streams, `udf_unicode_cksum()` for Unicode strings in big-endian byte order, and `udf_ea_cksum()` for the 48-byte extended-attribute checksum region.

Filename translation is handled by `UDFTransName()`. It walks a Unicode input name, replaces illegal or nonprintable characters with `_`, tracks short extensions, truncates to `MAXLEN`, and appends `#` plus a four-hex-digit Unicode CRC when the name needed modification or truncation. With the default `UNIX` path, only NUL and slash are illegal; OS/2, Windows, and Mac variants are still present behind preprocessor branches.

Risk areas include caller-managed buffer sizing, limited validation of compressed Unicode streams, and the use of OSTA reference-era translation rules. The kernel fallback `isprint()` is ASCII-like, and the name transformation intentionally changes names while preserving uniqueness through CRC suffixes.
