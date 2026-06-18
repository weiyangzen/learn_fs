# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.h

Read completely: 44 lines.

Declares the OSTA helper interface used by UDF code. It defines `unicode_t` as `uint16_t`, `byte` as `uint8_t`, sets default platform macros to `UNIX`, and sets default `MAXLEN` to 255.

Exported functions cover CS0 Unicode compression/decompression, byte and Unicode CRCs, extended-attribute checksums, OSTA filename translation, and null-terminated Unicode string length.

The header is simple but globally affects `udf_osta.c` behavior through the `UNIX` and `MAXLEN` defaults, so build environments that define alternate platform macros change filename legality and truncation rules.
