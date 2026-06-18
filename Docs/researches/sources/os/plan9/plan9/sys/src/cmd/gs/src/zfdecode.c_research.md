# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfdecode.c

## Purpose
Registers additional decoding and predictor filters, plus ASCII85 encode/decode support.

## Key Functions
- `zA85E()` and `zA85D()` create ASCII85 encode/decode filters.
- `zcf_setup()` reads CCITT fax parameters.
- `zCFD()` creates `CCITTFaxDecode`.
- `filter_read_predictor()` optionally cascades decompression with PixelDifference or PNG predictor decode filters.
- `zlz_setup()` reads LZW/GIF-style parameters.
- `zLZWD()` creates `LZWDecode`.
- `zpd_setup()` and `zpp_setup()` parse PixelDifference and PNG predictor dictionaries.

## Important Behavior
- Predictor values 0/1 mean identity; 2 selects componentwise differencing; 10-15 select PNG prediction.
- Predictor cascades mark the compression stream temporary and propagate `CloseSource`.
- Pixel and PNG setup validate color counts, columns, and power-of-two `BitsPerComponent`.

## Research Notes
Shares setup routines with encoder-side support in `zfilter2.c`.
