# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcllzw.c

Provides LZW stream prototypes for RAM-based command-list compression and decompression.

Key behavior:
- Defines static encoder and decoder `stream_LZW_state` prototypes.
- `gs_cl_lzw_init` initializes both states with LZW defaults and assigns the encode/decode stream templates.
- `clist_compressor_state` returns the encoder prototype.
- `clist_decompressor_state` returns the decoder prototype.

Dependencies:
- Uses Ghostscript stream/filter definitions from `strimpl` through `gxclmem.h` and LZW stream templates from `slzwx.h`.
- Called by `gxclmem.c` when opening compressible in-memory command-list files.

Research notes:
- The `mem` argument to `gs_cl_lzw_init` is unused; allocation happens later when memfiles copy these prototypes into GC-managed stream state objects.
