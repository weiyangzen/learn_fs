# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcparam.c

Optional compressor parameter-default and helper routines.

Key points:
- `jpeg_add_quant_table` scales caller-provided base quantization tables, clamps values, optionally enforces baseline range, and marks tables unsent.
- `jpeg_set_linear_quality`, `jpeg_quality_scaling`, and `jpeg_set_quality` implement IJG’s default luminance/chrominance quant tables and 0-100 quality curve.
- `add_huff_table` copies and lightly validates Huffman table counts/symbols.
- `std_huff_tables` installs JPEG standard 8-bit luminance/chrominance DC/AC tables.
- `jpeg_set_defaults` allocates permanent `comp_info`, sets default precision, quality, Huffman tables, arithmetic conditioning, scan/raw/entropy/DCT/restart/JFIF defaults, and then selects a default JPEG colorspace.
- `jpeg_default_colorspace` maps input colorspaces to preferred JPEG colorspaces.
- `jpeg_set_colorspace` sets component count, IDs, sampling factors, quant/Huffman table assignments, and JFIF/Adobe marker flags for grayscale, RGB, YCbCr, CMYK, YCCK, or unknown data.
- With progressive support, `jpeg_simple_progression` allocates/reuses permanent scan-script storage and fills a recommended progressive scan sequence.

Dependencies and interactions:
- Public setup layer used by `cjpeg`, normal applications, and transcoding parameter copying.
- Feeds tables and component metadata consumed by `jcmaster.c`, `jcmarker.c`, `jcdctmgr.c`, and entropy encoders.

Risk notes:
- All mutating helpers require `CSTATE_START`.
- Standard Huffman tables are explicitly only valid for 8-bit precision; higher precision forces optimization.
- `jpeg_set_colorspace` overwrites component assignments, so custom sampling/table choices must be applied after it.
