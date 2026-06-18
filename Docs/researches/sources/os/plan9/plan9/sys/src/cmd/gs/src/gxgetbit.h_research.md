# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxgetbit.h

## Purpose
Defines the parameter interface and helper declarations for the device `get_bits_rectangle` procedure.

## Main Types
- `gs_get_bits_options_t`: alias of `gx_bitmap_format_t`.
- `gs_get_bits_params_t`: options, up to 32 data plane pointers, returned X offset, and raster.

## Contract
- Devices update `options` to the actual chosen bitmap format.
- If input options are zero, the device must report supported options and return an error.
- All devices must support at least one option in each bitmap-format group and `GB_COLORS_NATIVE`.
- Default implementation only supports a limited set: 8-bit depth, chunky packing, return-copy behavior, and requires chunky packing support.

## Declared Helpers
- `gx_get_bits_return_pointer`: tries to satisfy the request by returning a pointer into stored data.
- `gx_get_bits_copy`: satisfies the request by copying from source bytes into caller-requested output form.

## Integration
Used by device implementors and clients needing bitmap extraction without depending on the full driver-client header surface.
