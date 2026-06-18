# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmem.c

## Role

Generic Ghostscript memory bitmap device implementation. It provides allocation, scan-line pointer setup, device construction helpers, color palette mapping, get-bits export, byte swapping for word-oriented devices, and memory-device identification.

## Main Interfaces

- `gdev_mem_device_for_bits` and `gdev_mem_word_device_for_bits` map bit depths to prototype memory devices.
- `gs_device_is_memory` identifies memory devices by the distinctive `draw_thin_line` procedure.
- `gs_make_mem_device` and `gs_make_mem_mono_device` initialize memory devices from prototypes and optional target devices.
- `gdev_mem_bits_size`, `gdev_mem_line_ptrs_size`, `gdev_mem_data_size`, and `gdev_mem_max_height` compute bitmap storage requirements.
- `mem_open`, `gdev_mem_open_scan_lines`, `gdev_mem_set_line_ptrs`, and `mem_close` manage bitmap/line-pointer allocation and cleanup.
- `mem_get_bits_rectangle` exports rectangular pixel data via Ghostscript get-bits negotiation.
- `mem_word_get_bits_rectangle` handles little-endian word-oriented byte order by swapping before and after export.
- `mem_mapped_map_rgb_color` and `mem_mapped_map_color_rgb` perform palette lookup for mapped 2/4/8-bit devices.

## Data Model

A memory device stores contiguous scan lines plus a line-pointer table. Planar devices are accounted for in size and line-pointer setup, but normal `mem_open` rejects `num_planes != 0`; planar open is handled in `gdevmpla.c`.

## Important Behavior

- Monobit devices default to white `0`, black `1`, unless target color semantics change this through `gdev_mem_mono_set_inverted`.
- `gdev_mem_max_height` has a transparency-aware estimation path using `ESTIMATED_PDF14_ROW_SPACE`.
- GC relocation adjusts `base`, `line_ptrs`, and palette references, with special handling for foreign buffers.
- `mem_get_bits_rectangle` first offers pointer return when compatible, then falls back to copying.

## Risks and Edge Cases

- Storage-size calculations use `ulong` and later cast to `uint` in allocation; overflow is guarded only at open.
- Palette lookup is nearest-match by simple component absolute-difference sum, not perceptual.
- Word byte swapping mutates the device buffer temporarily, so callers depend on no concurrent access.
