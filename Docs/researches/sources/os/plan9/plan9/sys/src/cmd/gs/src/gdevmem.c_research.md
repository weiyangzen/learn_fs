# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmem.c

Generic Ghostscript bitmap-backed memory device implementation.

- Defines GC descriptors and relocation for `gx_device_memory`, including owned/foreign bitmap storage, line-pointer tables, and palette strings.
- Provides standard monobit palettes: black-white and white-black variants for inverted 1-bit memory devices.
- Maps bit depths to memory-device prototypes via `gdev_mem_device_for_bits` and word-oriented prototypes via `gdev_mem_word_device_for_bits`; supported depths include 1, 2, 4, 8, 16, 24, 32, 40, 48, 56, and 64.
- Uses `draw_thin_line == mem_draw_thin_line` as the marker for `gs_device_is_memory`.
- `gs_make_mem_device` and `gs_make_mem_mono_device` initialize memory devices, optionally forwarding color mapping to a target device and handling 1-bit inversion.
- Size helpers compute bitmap storage, line pointer storage, total data size, and maximum height, including a special PDF 1.4 transparency estimate path.
- `mem_open` rejects planar devices and delegates to `gdev_mem_open_scan_lines`; scan-line setup supports contiguous bitmap-plus-pointer storage or separately allocated line pointers.
- `mem_get_bits_rectangle` returns native chunky pixels by pointer when possible or copies through Ghostscript get-bits helpers.
- Little-endian word-oriented devices use `mem_swap_byte_rect` and `mem_word_get_bits_rectangle` to swap word byte order around get-bits calls.
- Palette-mapped devices implement nearest-palette RGB/gray lookup in `mem_mapped_map_rgb_color` and decode indices in `mem_mapped_map_color_rgb`.
- Risk notes: relocation logic adjusts line pointers relative to moved base storage; incorrect ownership flags would corrupt GC relocation/free behavior. `gdev_mem_max_height` is exact only outside the PDF transparency estimate path.
