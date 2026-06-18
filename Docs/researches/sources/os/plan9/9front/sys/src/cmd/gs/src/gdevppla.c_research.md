# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevppla.c

Helper implementation for printer devices that can use planar buffering instead of chunky memory buffering.

Key behavior:
- `gdev_prn_set_procs_planar` replaces a printer device's buffer creation and sizing callbacks with planar-aware variants.
- `gdev_prn_open_planar` conditionally installs planar buffer callbacks before calling `gdev_prn_open`.
- `gdev_prn_get_params_planar` and `gdev_prn_put_params_planar` wrap generic printer parameter handling with a `UsePlanarBuffer` boolean for multi-component devices.
- `gdev_prn_set_planar` configures a memory device into 3- or 4-plane layout by deriving a per-plane depth, rounding it up to a power of two, and assigning shifts so the most significant component plane comes first.
- `gdev_prn_create_buf_planar` creates the default buffer device and then converts memory buffers to planar layout.
- `gdev_prn_size_buf_planar` computes planar buffer bit storage, line-pointer storage, and raster requirements for full-page/band buffering.

Notable dependencies:
- Generic printer framework from `gdevprn.h`.
- Planar memory-device support from `gdevmpla.h`.
- Public declarations from `gdevppla.h`.

Research notes:
- The helper is narrow and intentionally parameter-driven; concrete printer drivers opt in by calling these functions.
- Planar buffering is restricted to 3- or 4-component devices; other component counts return `rangecheck`.
