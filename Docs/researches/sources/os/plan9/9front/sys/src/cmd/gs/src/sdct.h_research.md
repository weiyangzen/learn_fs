# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdct.h

Defines common DCT/JPEG stream state. It models IJG libjpeg allocations through immovable Ghostscript memory blocks tracked by `jpeg_block_t`, wraps common JPEG error/longjmp/memory/parameter fields, and defines separate compression and decompression data records.

`stream_DCT_state` stores common stream state, marker data, `QFactor`, `ColorTransform`, `NoMarker`, JPEG allocation memory, a union pointer to compress/decompress/common data, scan line size, and phase. It declares DCT encode/decode templates and the shared defaults function.

Dependencies include `setjmp.h`, libjpeg public structs, Ghostscript stream implementation headers, and memory/GC descriptor macros.

This is the central type contract for Ghostscript DCT filters.
