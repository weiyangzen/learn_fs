# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/zmod.h

`zmod.h` declares the public kernel interface for zmod, an in-kernel RFC 1950-compatible compression/decompression library. The implementation lives under `usr/src/uts/common/zmod/`.

The header mirrors common zlib status and configuration constants: success, stream end, dictionary needed, errno-style failure, stream/data/memory/buffer/version errors, and compression levels from no compression through best speed, best compression, and default compression.

The exported routines are `z_uncompress()`, `z_compress()`, `z_compress_level()`, and `z_strerror()`. The compress/uncompress functions take destination pointer and destination-size pointer plus source pointer and source size, matching the common zlib pattern where the destination size is both input capacity and output length.

This is a small ABI header used by kernel consumers that need compressed data handling without depending on userland zlib.
