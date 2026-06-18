# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdevn.c

Ghostscript example DeviceN and spot-color process-model device implementation. It provides utility routines for DeviceN parameter handling, colorant-name lookup, component mapping, packed raster repacking, and example `spotcmyk`/`devicen` printer devices that write raw component files and PCX previews.

Key behavior:
- Converts Gray/RGB/CMYK source color spaces into DeviceN component arrays using the current separation-order map.
- `bpc_to_depth` computes packed device depth for component count and bits per component.
- `check_pcm_and_separation_names` and `devn_get_color_comp_index` resolve process colorants and spot separations, optionally auto-adding new spot colorants.
- `devn_get_params`, `devn_put_params`, and `devn_printer_put_params` manage `SeparationColorNames`, `SeparationOrder`, `Separations`, and `MaxSeparations`, including rollback for standard printer parameter failures.
- Defines two devices:
  - `spotcmyk`: 1-bit CMYK plus optional spot colors.
  - `devicen`: 8-bit component DeviceN-style example device.
- `spotcmyk_encode_color` and `spotcmyk_decode_color` pack/unpack component values into `gx_color_index`.
- `repack_data` extracts selected bit fields from packed pixels into process-color or spot-color output streams.
- `spotcmyk_print_page` writes process color data to the main output, writes each spot color to sibling files named with `sN`, then converts those raw files to `.pcx`.
- Embedded PCX writer builds headers, palettes, planar/chunky layouts, and RLE-compressed image rows for a limited set of bit-depth/component combinations.

Notable dependencies:
- Ghostscript printer, parameter, color-rendering, and equivalent-color APIs: `gdevprn.h`, `gsparam.h`, `gscrd.h`, `gdevdcrd.h`, `gxdcconv.h`, `gsequivc.h`.
- Shared declarations from `gdevdevn.h`.

Research notes:
- The file labels these as example devices; output behavior is demonstrative rather than a polished production image format pipeline.
- `devn_put_params` allocates new separation-name buffers when `SeparationColorNames` changes; ownership is tracked for GC relocation, but old names are not visibly freed during replacement.
- In `spotcmyk_print_page`, early returns after PCX conversion failures bypass the common cleanup label, leaking temporary buffers.
- `pcx_write_rle` compares `data != *from || from == end`; because C evaluates left-to-right, it may dereference `from` when `from == end`.
