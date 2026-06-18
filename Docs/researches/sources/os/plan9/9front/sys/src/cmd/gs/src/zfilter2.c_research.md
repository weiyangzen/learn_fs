# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilter2.c

## Purpose
Adds encoder-side CCITT Fax and LZW filters and implements predictor cascade support for write filters.

## Key Functions
- `zCFE()` creates `CCITTFaxEncode` after reading shared CCITT parameters via `zcf_setup()`.
- `filter_write_predictor()` optionally wraps compression output with PixelDifference or PNG predictor encode filters.
- `zLZWE()` creates `LZWEncode` with optional predictor processing.

## Important Behavior
- Predictor handling mirrors `filter_read_predictor()` in `zfdecode.c`.
- Predictor 0/1 means no predictor; 2 selects PixelDifference; 10-15 selects PNG prediction.
- Cascaded predictor setup saves original operands for error recovery and marks the compression stream temporary so close semantics remain correct.

## Research Notes
This file is intentionally small because most parameter parsing is shared with decoder-side helpers in `zfdecode.c`.
