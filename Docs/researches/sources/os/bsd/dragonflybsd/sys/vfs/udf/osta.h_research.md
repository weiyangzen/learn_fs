# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/osta.h

Prototype and compatibility header for OSTA UDF helper routines.

Key responsibilities:
- Defaults the platform macro to `UNIX` if no platform is selected.
- Defaults `MAXLEN` to 255 for translated filenames.
- Defines the helper types `unicode_t` as unsigned 16-bit and `byte` as unsigned 8-bit.
- Declares CS0 compression/decompression, byte checksum, Unicode checksum, and optional filename translation functions.

Dependencies:
- Expects the compiler's `unsigned short` and `unsigned char` sizes to match the documented UDF helper assumptions.
- Included by both `osta.c` and UDF VFS/vnode code.

Notable risks:
- Type definitions are intentionally simple and predate fixed-width typedefs; portability assumes DragonFly's target ABI.
- `UDFTransName` is declared even though the implementation is conditional in `osta.c`.
