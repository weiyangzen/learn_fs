# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage.c

Generic Ghostscript image support shared by multiple image types.

Key behavior:
- Provides structure descriptors for common, data, and pixel image objects.
- Initializes common image fields, explicit-data image defaults, and pixel image defaults.
- `gx_image_enum_common_init` initializes common enumerator metadata and derives plane counts, widths, and depths for chunky, component-planar, and bit-planar input formats.
- Client helpers forward image data to an enumerator: `gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, and `gx_image_end`.
- Provides dummy stream serialization handlers for image types that cannot be serialized.
- Implements compact stream serialization/deserialization of generic pixel image parameters, including image matrix, bits per component, format, decode arrays, interpolation, and CombineWithColor.
- Provides variable-length unsigned integer encoding helpers and default image matrix detection/setup.

Notable dependencies:
- Color-space APIs from `gscspace.h`.
- Matrix and stream helpers from `gsmatrix.h` and `stream.h`.
- Image type definitions from `gxiparam.h`.

Research notes:
- Serialization is designed for Ghostscript banding/internal streams, not external image formats.
- The decode serialization is compact and special-cases default, inverted default, `(0,V)`, and `(U,V)` decode pairs.
- 12-bit pixel serialization is accepted for some formats; 16-bit support is handled elsewhere through unpack procedure availability.
