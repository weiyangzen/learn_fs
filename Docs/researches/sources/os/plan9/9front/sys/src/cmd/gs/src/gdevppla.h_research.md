# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.h

Public header for planar-buffer support in Ghostscript printer devices.

Key contents:
- Declares `gdev_prn_set_procs_planar()` to replace printer buffer callbacks with planar variants.
- Declares `gdev_prn_open_planar()` to conditionally enable planar buffering before opening a printer.
- Declares `gdev_prn_get_params_planar()` and `gdev_prn_put_params_planar()` for adding `UsePlanarBuffer` to a printer's parameter surface.
- Declares `gdev_prn_create_buf_planar()` and `gdev_prn_size_buf_planar()` as planar replacements for default buffer-device creation and sizing.

Notable dependencies:
- Requires `gdevprn.h` in the including compilation unit for `gx_device`, `gx_render_plane_t`, `gx_device_buf_space_t`, `gs_memory_t`, and Ghostscript boolean types.

Research notes:
- This header is a thin opt-in extension for printer drivers; the implementation lives in `gdevppla.c`.
