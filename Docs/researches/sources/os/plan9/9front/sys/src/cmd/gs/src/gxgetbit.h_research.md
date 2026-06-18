# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxgetbit.h

Defines the parameter interface and helpers for the `get_bits_rectangle` device procedure.

Key definitions:
- `gs_get_bits_options_t` aliases `gx_bitmap_format_t`.
- `gs_get_bits_params_t` carries accepted/chosen format options, up to 32 data plane pointers, returned X offset, and raster.
- Documents that devices update `options` with the actual chosen format, one option per group.
- Documents that `options == 0` is a capability query and should return supported options with an error.

Key declarations:
- `gx_get_bits_return_pointer` tries to implement `get_bits_rectangle` by returning a pointer into stored device data.
- `gx_get_bits_copy` implements `get_bits_rectangle` by copying from stored device data.

Dependencies:
- Includes `gxbitfmt.h`.
- Uses `gx_device` and byte/raster types from Ghostscript core headers.

Research notes:
- This header isolates bitmap retrieval option details so most device users do not need recompilation when options change.
- Default support assumes 8-bit depth, chunky packing, and copy return unless devices override more formats.
