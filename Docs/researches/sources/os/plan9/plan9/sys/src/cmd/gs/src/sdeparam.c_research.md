# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdeparam.c

Parameter get/put support for `DCTEncode`.

It defines encode-specific scalar parameters:

- `Columns`, `Rows`, `Colors`, `Marker`, `NoMarker`, `Resync`, and `Blend`.

Get path:

- Reports common DCT parameters, encode scalars, horizontal/vertical sampling factors, quantization tables, and Huffman tables.
- Builds a temporary default compression state when only non-default values are requested.
- Notes unresolved `NYI`/`Blend` handling in comments.

Put path:

- Requires valid image dimensions and component count; rejects two-component JPEG and invalid ranges.
- Reads common DCT parameters, initializes IJG defaults, optional Huffman and quantization tables, and applies `QFactor` when no explicit quant tables are supplied.
- Selects IJG color spaces and Adobe marker `ColorTransform` behavior for grayscale, RGB, and CMYK/YCCK.
- Reads `HSamples` and `VSamples`, validates factors 1 through 4, disables JFIF/Adobe automatic markers, sets restart interval, and enforces sample-count limits unless `Relax` is enabled.

This is JPEG encoder parameter handling, not filesystem code.
