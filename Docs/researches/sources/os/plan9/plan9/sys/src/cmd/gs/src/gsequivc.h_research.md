# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsequivc.h

## Role

`gsequivc.h` declares data structures and the public helper for collecting equivalent CMYK colors for spot colorants.

## Types

`cmyk_color` stores validity plus `frac` C/M/Y/K components.

`equivalent_cmyk_color_params` stores an all-valid flag and an array of per-separation `cmyk_color` entries sized to `GX_DEVICE_MAX_SEPARATIONS`.

## API

Declares:

- `update_spot_equivalent_cmyk_colors(gx_device *, const gs_state *, gs_devn_params *, equivalent_cmyk_color_params *)`

## Dependencies

Requires `bool`, `frac`, `GX_DEVICE_MAX_SEPARATIONS`, `gx_device`, `gs_state`, and `gs_devn_params` definitions from surrounding Ghostscript device/color headers.

## Integration Notes

Device implementations that need spot equivalent colors embed `equivalent_cmyk_color_params` in their device state and call the update helper when Separation/DeviceN color spaces are installed.

## Risks

The header exposes fixed-size storage tied to the maximum device separation count. Device code must initialize validity flags and keep the separation-name list synchronized with the equivalent-color array.
