# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevppla.c

This file implements helper support for Ghostscript printer devices that want planar buffering. It is a small adapter layer over the generic printer buffer hooks and memory planar-device support.

`gdev_prn_set_procs_planar` replaces a printer device's buffer creation and sizing procedures with `gdev_prn_create_buf_planar` and `gdev_prn_size_buf_planar`. `gdev_prn_open_planar` conditionally installs those hooks based on a `UsePlanarBuffer` boolean before calling `gdev_prn_open`.

`gdev_prn_get_params_planar` and `gdev_prn_put_params_planar` augment standard printer get/put parameter handling with the `UsePlanarBuffer` parameter. The put path only reads the parameter for multi-component devices, delegates ordinary printer params to `gdev_prn_put_params`, and commits the new boolean only if parameter handling succeeds.

The private helper `gdev_prn_set_planar` configures a `gx_device_memory` as a planar memory device. It supports 3- or 4-component color, computes per-plane depth from total color depth, rounds depth up to a power of two if necessary, and orders planes so the most significant plane is emitted first.

`gdev_prn_create_buf_planar` first uses `gx_default_create_buf_device`, then converts memory buffer devices to planar mode. `gdev_prn_size_buf_planar` mirrors the memory sizing calculation for planar layout, computing bit storage, line pointer storage, and raster size for the first plane.

Filesystem relevance: none. This is raster memory layout support for printer buffering.
