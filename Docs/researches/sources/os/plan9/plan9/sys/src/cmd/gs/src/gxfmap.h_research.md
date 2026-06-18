# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfmap.h

## Purpose
Defines cached fraction-to-fraction transfer maps used in Ghostscript color processing.

## Main Type
`gx_transfer_map` contains:
- reference-count header,
- legacy `proc`,
- newer `closure`,
- changing `id`,
- cached `frac values[transfer_map_size]`.

## Constants
- `log2_transfer_map_size` is 8.
- `transfer_map_size` is 256.
- Interpolation is enabled when `log2_transfer_map_size <= 8`.

## Public/Declared Operations
- `gx_set_identity_transfer`: initializes identity map.
- `gx_color_frac_map`: interpolating map helper when enabled.
- `gx_map_color_frac`: maps a `frac` through a transfer map.
- `gx_map_color_float`: maps a float by table lookup.
- `gs_mapped_transfer`: closure-style lookup function.
- `gs_identity_transfer`: identity transfer procedure.

## Integration
Used by color transfer, black generation, and undercolor removal paths. It depends on `gxfrac.h`, transfer-map closure definitions, reference counting, and GC descriptors.
