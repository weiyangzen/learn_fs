# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmpla.c

Any-depth planar memory-device implementation.

- Public entry point `gdev_mem_set_planar` validates plane count, per-plane depth, shift overlap, supported memory depth, and total depth before replacing chunky drawing procs with planar-aware ones.
- `mem_planar_open` rejects non-planar devices and uses normal memory scan-line allocation.
- Drawing operations temporarily patch `gx_device_memory` fields to expose one plane at a time to the appropriate standard memory-device prototype.
- Implements planar `fill_rectangle`, `copy_mono`, `copy_color`, `strip_tile_rectangle`, and `get_bits_rectangle`.
- `copy_color` extracts each plane from chunky input into a fixed stack buffer, chunking wide transfers as needed, then calls the plane-depth copy routine.
- `strip_tile_rectangle` can split monochrome colored tiles by plane but punts colored tiles to the default implementation.
- `planar_to_chunky` repacks planar storage back into native chunky pixels, with optimized direct byte-per-component cases for 3- and 4-plane 8-bit components.
- `mem_planar_get_bits_rectangle` can return a single requested plane directly, otherwise falls back to chunky format and may copy through an intermediate buffer for unsupported get-bits options.
- Risk notes: procedure patching relies on careful save/restore of depth, base, raster, line pointers, and `copy_mono`; errors in intermediate routines could leave device state inconsistent.
