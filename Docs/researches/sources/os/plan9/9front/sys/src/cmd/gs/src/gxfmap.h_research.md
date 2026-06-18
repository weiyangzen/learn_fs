# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfmap.h

Defines cached color transfer-map representation and lookup helpers.

Key definitions:
- `gx_transfer_map` stores a reference-count header, legacy mapping proc, closure, changing ID, and `frac` lookup table.
- Transfer maps use `transfer_map_size == 256`.
- `public_st_transfer_map` declares GC traversal over the mapping closure/proc state.
- `gx_set_identity_transfer` initializes identity maps.
- `gx_map_color_frac` maps fractional color components through the cache, interpolating when the table is small enough.
- `gx_map_color_float` maps float inputs through the cache.
- Declares `gs_mapped_transfer` and `gs_identity_transfer`.

Dependencies:
- Includes `gsrefct.h`, `gsstype.h`, `gxfrac.h`, and `gxtmap.h`.
- `gx_color_frac_map` implementation is in `gxcmap.c`.

Research notes:
- This is used by imager/color state for transfer functions, black generation, and undercolor removal.
- The comments note an intermediate migration from `proc` to `closure`.
