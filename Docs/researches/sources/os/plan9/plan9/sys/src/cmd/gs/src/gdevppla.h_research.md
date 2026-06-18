# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.h

This header declares the planar printer buffering helper API implemented by `gdevppla.c`.

The exposed functions are:

- `gdev_prn_set_procs_planar(gx_device *pdev)`, which installs planar buffer procedure hooks in a printer device.
- `gdev_prn_open_planar(gx_device *pdev, bool upb)`, which conditionally enables planar buffering and then opens the printer.
- `gdev_prn_get_params_planar(...)` and `gdev_prn_put_params_planar(...)`, which add the `UsePlanarBuffer` parameter around the standard printer parameter API.
- `gdev_prn_create_buf_planar(...)`, a replacement buffer-device creation hook for planar mode.
- `gdev_prn_size_buf_planar(...)`, a replacement buffer-size hook for planar mode.

The header notes that it requires `gdevprn.h` and is intended for printer devices that choose planar buffers instead of the default chunky memory buffer.

Filesystem relevance: none. It is a declaration-only printer/raster support header.
