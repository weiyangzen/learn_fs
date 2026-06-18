# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdeparam.c

Implements DCTEncode parameter read/write logic for the JPEG compression stream.

Key points:
- Defines scalar DCTEncode parameters: `Columns`, `Rows`, `Colors`, `Marker`, `NoMarker`, `Resync`, and `Blend`.
- `s_DCTE_get_params` reports JPEG image dimensions/components, marker settings, restart interval, shared DCT parameters, sampling factors, quantization tables, and Huffman tables.
- `dcte_get_samples` writes `HSamples`/`VSamples` arrays only when non-default values are needed unless all parameters are requested.
- `s_DCTE_put_params` validates required encode dimensions and color counts, applies common DCT parameters, initializes IJG defaults, installs tables, applies `QFactor`, and maps Ghostscript `ColorTransform` to IJG RGB/CMYK/YCC/YCCK behavior.
- `dcte_put_samples` enforces Adobe-style default sampling factors of 1 rather than IJG defaults, with range checks of 1..4.
- Disables IJG JFIF and Adobe marker writing because Ghostscript manages those marker choices itself.

Dependencies and interactions:
- Uses `sdct.h`, `sdcparam.h`, and `sjpeg.h` wrappers around IJG libjpeg.
- Closely coupled to `stream_DCT_state`, `jpeg_compress_data`, and common DCT parameter/table helpers.

Research relevance:
- This is the encode-side bridge between PostScript/PDF DCT filter dictionaries and the actual JPEG compressor state.
