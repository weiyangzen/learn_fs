# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdgbr.c

Implements default `get_bits` and `get_bits_rectangle` behavior, including conversion between native device pixels and standard Gray/RGB/CMYK representations.

`gx_default_get_bits` converts a one-scanline request into `get_bits_rectangle`, temporarily replacing `get_bits` with `gx_no_get_bits` to avoid recursion. `gx_default_get_bits_rectangle` does the reverse when possible, using `get_bits` for simple one-row native chunky requests, otherwise recursively pulling rows and calling `gx_get_bits_copy`.

`gx_get_bits_return_pointer` checks whether requested options are compatible with stored representation and, if alignment permits, returns direct pointers into stored data. `gx_get_bits_copy` handles direct bit copies, shifted bit copies through a memory device, planar extraction, and native/standard color conversion.

Conversion helpers map standard colors to native by using device color mapping and `encode_color`, and native to standard by using `map_color_rgb_alpha`. There is a dedicated 4-bit CMYK to 24-bit RGB fast path for common PCL usage.

Dependencies include bitmap sample load/store macros, memory devices, `gxgetbit.h`, luminance weights, and device color mapping procs.

Risks: option handling is complex and alignment-sensitive. Several paths allocate temporary row buffers. Only 8-bit standard output depth is supported for native-to-standard conversion, with rangecheck for unsupported cases.
