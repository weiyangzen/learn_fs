# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevmem.h

Defines Ghostscript memory devices, which are bitmap-backed forwarding devices.

- Memory devices support multiple bitmap formats:
  - 1-bit mono
  - 2/4/8-bit mapped color
  - 16/24-bit RGB
  - 32-bit CMYK
  - wider component layouts with small caches
- Distinguishes standard big-endian bitmap storage from word-oriented machine-order storage.
- Describes four storage allocation modes:
  - allocate bits and line pointers via `bitmap_memory`
  - caller supplies bitmap, device allocates line pointers
  - device allocates only line pointers and caller sets them later
  - caller owns both bitmap and line pointers
- Defines `gx_device_memory_s`, extending `gx_device_forward_common`.
- Key fields:
  - `raster`, `base`, `line_ptrs`
  - bitmap and line-pointer allocators
  - `foreign_bits`, `foreign_line_pointers` GC flags
  - planar-device descriptors
  - palette
  - cached packed-color expansions for 24/40/48/56/64-bit cases
  - alpha-buffer mapping/scaling fields
- Defines `mem_device_init_private` initializer data.
- Declares size/raster helpers:
  - `gdev_mem_bits_size`
  - `gdev_mem_line_ptrs_size`
  - `gdev_mem_data_size`
  - `gdev_mem_max_height`
  - `gdev_mem_raster`
- Declares prototype lookup:
  - `gdev_mem_device_for_bits`
  - `gdev_mem_word_device_for_bits`
- Declares constructors:
  - `gs_make_mem_mono_device`
  - `gs_make_mem_device`
  - `gs_make_mem_abuf_device`
  - `gs_make_mem_alpha_device`
- Declares scanline setup:
  - `gdev_mem_open_scan_lines`
  - `gdev_mem_set_line_ptrs`
- Declares tests:
  - `gs_device_is_memory`
  - `gs_device_is_abuf`

Important invariant: planar devices require `color_info.depth` to equal the sum of plane depths.
