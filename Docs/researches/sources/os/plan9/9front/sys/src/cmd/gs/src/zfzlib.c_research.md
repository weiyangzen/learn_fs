# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfzlib.c

## Purpose
Registers zlib and Flate encode/decode filters for the PostScript interpreter.

## Key Functions
- `filter_zlib()` initializes `stream_zlib_state` and reads optional `Effort`.
- `zzlibE()` and `zzlibD()` create raw `zlibEncode`/`zlibDecode` filters.
- `zFlateE()` and `zFlateD()` create `FlateEncode`/`FlateDecode`, with predictor chaining.

## Important Behavior
- `Effort` is accepted from filter dictionaries in the range `-1..9`.
- Flate filters route through predictor-aware helper paths, unlike raw zlib filters.
- Registers four filter operators in `zfzlib_op_defs`.

## Research Notes
Thin interpreter wrapper over stream templates from Ghostscript’s zlib integration.
