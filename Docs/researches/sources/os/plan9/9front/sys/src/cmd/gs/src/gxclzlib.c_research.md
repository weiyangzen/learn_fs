# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclzlib.c

zlib stream-state initialization for RAM-based command-list band lists.

Key behavior:
- Holds static prototype `stream_zlib_state` objects for compression and decompression.
- `gs_cl_zlib_init` initializes both states with zlib defaults, disables zlib wrapper bytes, and installs encode/decode stream templates.
- `clist_compressor_state` and `clist_decompressor_state` return the prepared prototype stream states.

Notable dependencies:
- Ghostscript stream/zlib integration from `szlibx.h`.
- RAM clist infrastructure from `gxclmem.h`.

Research notes:
- This file only supplies reusable stream prototypes; actual clist code copies/uses these states elsewhere.
- It must be compiled with access to the zlib source include directory.
