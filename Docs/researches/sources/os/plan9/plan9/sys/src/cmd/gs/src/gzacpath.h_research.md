# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzacpath.h

Declares the clipping path accumulator device. `gx_device_cpath_accum` is a Ghostscript device that accumulates a rectangle list while optionally clipping to a band boundary rectangle.

Exports:
- `gx_cpath_accum_begin`
- `gx_cpath_accum_set_cbox`
- `gx_cpath_accum_end`
- `gx_cpath_accum_discard`
- `gx_cpath_intersect_path_slow`

This supports banded rendering and clipping path construction. Its role is internal graphics geometry, not OS file handling.
