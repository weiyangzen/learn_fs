# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdecode.c

## Purpose
Registers additional decoding and predictor filters, plus ASCII85 encode/decode support.

## Key Functions
- `zA85E()` and `zA85D()` create ASCII85 encode/decode filters.
- `zcf_setup()` reads CCITT fax parameters through the generic parameter-list API.
- `zCFD()` creates `CCITTFaxDecode`.
- `filter_read_predictor()` optionally cascades decompression with PixelDifference or PNG predictor decode filters.
- `zlz_setup()` reads LZW/GIF-style parameters such as `EarlyChange`, `InitialCodeLength`, bit order, and block-data mode.
- `zLZWD()` creates `LZWDecode`, including LanguageLevel 3 `LowBitFirst` and `UnitSize` aliases.
- `zpd_setup()`, `zPDiffE()`, and `zPDiffD()` handle PixelDifference predictor setup.
- `zpp_setup()`, `zPNGPE()`, and `zPNGPD()` handle PNG predictor setup.

## Important Behavior
- Predictor values 0/1 mean identity; 2 selects componentwise differencing; 10-15 select PNG prediction.
- Predictor cascades mark the compression stream temporary and propagate `CloseSource`.
- Pixel and PNG setup validate color counts, columns, and power-of-two `BitsPerComponent`.
- The op table includes both encode and decode entries for ASCII85 and predictor filters.

## Research Notes
This file shares setup routines with `zfilter2.c` for encoder-side LZW and CCITT handling.
