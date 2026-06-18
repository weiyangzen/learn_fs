# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage.c

Generic Ghostscript image support shared by multiple image types.

Key behavior:
- Defines structure descriptors for common, data, and pixel image objects.
- Initializes common image matrices, explicit-data defaults, pixel-image defaults, formats, decode arrays, color spaces, and `CombineWithColor`.
- `gx_image_enum_common_init` initializes common enumerator metadata and derives plane counts, widths, and depths for chunky, component-planar, and bit-planar formats.
- Provides client wrappers for feeding data and ending images: `gx_image_data`, `gx_image_plane_data`, `gx_image_plane_data_rows`, `gx_image_flush`, `gx_image_planes_wanted`, and `gx_image_end`.
- Supplies dummy stream serialization functions for image types that cannot be serialized.
- Implements compact stream serialization/deserialization of generic pixel image parameters, including matrix, bits/component, format, decode arrays, interpolation, and CombineWithColor.
- Provides variable-length unsigned integer stream encoding and helpers for default ImageMatrix detection/setup.

Notable dependencies:
- Color-space APIs from `gscspace.h`.
- Matrix and utility helpers from `gsmatrix.h` and `gsutil.h`.
- Stream APIs from `stream.h`.
- Image type definitions from `gxiparam.h`.

Research notes:
- Serialization is for Ghostscript internal/banding streams, not image file formats.
- Decode serialization special-cases default, inverted default, `(0,V)`, and `(U,V)` forms to keep streams compact.
- Generic serialization accepts 12-bit image parameters for some formats; actual 12/16-bit unpack availability is controlled elsewhere.
