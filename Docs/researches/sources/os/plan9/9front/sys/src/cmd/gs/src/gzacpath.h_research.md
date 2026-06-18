# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzacpath.h

Declares the clipping-path accumulator device interface.

Key points:
- Defines `gx_device_cpath_accum`, a device that accumulates clip rectangles into a `gx_clip_list`.
- Stores allocator, clip box, bounding box, and accumulated list.
- Used to clip accumulated clipping paths to band boundaries during band-list rendering.
- Declares begin, set clipping box, end, discard, and slow path intersection APIs.
- `gx_cpath_accum_end` releases old clipping-path contents before installing the accumulated result.

Research notes:
- This is infrastructure for converting device output into clipping-region data.
- It depends on device and clipping-path internals rather than public PostScript APIs.
