# File Research: sources/os/bsd/openbsd-src/sbin/savecore/compress.h

This header declares the compression abstraction used by `savecore`’s `.Z` writer.

Key contents:
- `struct z_info`: timestamp, CRC, header length, and input/output byte counters.
- `Z_BUFSIZE` buffer-size constant.
- `enum program_mode` and global `pmode` for compatibility with compressor code.
- Exit-code constants: `SUCCESS`, `FAILURE`, `WARNING`.
- Function prototypes for generic `z_*`, gzip `gz_*`, LZH `lzh_*`, and null-compression backends.

Integration:
- `zopen.c` implements the `.Z` LZW subset used by `savecore`.
- Several prototypes are compatibility-oriented and are not all implemented in this small `savecore` build.

Risk notes:
- The header exposes a broad compressor API compared with the small local implementation.
- It declares a global `pmode` in a header, which is acceptable only if included in a controlled legacy build context.
