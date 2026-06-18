# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcllzw.c

## Purpose
Provides LZW compressor/decompressor prototype states for RAM-backed command-list files.

## Main Responsibilities
- Defines static LZW encode/decode state prototypes.
- Initializes them in `gs_cl_lzw_init`.
- Exposes prototype pointers through:
  - `clist_compressor_state`
  - `clist_decompressor_state`

## Key Implementation Details
- Uses `s_LZW_set_defaults` for both states.
- Assigns `s_LZWE_template` to the compressor and `s_LZWD_template` to the decompressor.
- The `mem` argument to `gs_cl_lzw_init` is unused in this file.

## Dependencies
- `gxclmem.h` declares the compressor/decompressor accessors.
- `slzwx.h` supplies LZW stream templates.

## Research Notes
This file is deliberately small. It decouples `gxclmem.c` from direct static construction of LZW stream states.
