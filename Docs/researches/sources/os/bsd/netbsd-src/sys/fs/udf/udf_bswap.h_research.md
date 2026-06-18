# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_bswap.h

Read completely: 76 lines.

Defines endian access helpers for UDF on-disc little-endian fields. On big-endian machines, `udf_rw16()`, `udf_rw32()`, and `udf_rw64()` inline to byte-swap operations. On little-endian machines, the same names are casts/no-ops.

The header is intentionally small but pervasive: UDF code uses these helpers both when reading on-disc fields and when writing values back into descriptor structures.

Risk is mostly misuse risk. Because the helpers are named as bidirectional read/write converters, callers must apply them consistently exactly once at every on-disc boundary.
