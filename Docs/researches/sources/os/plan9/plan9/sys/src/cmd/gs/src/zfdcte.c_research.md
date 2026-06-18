# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfdcte.c

## Purpose
Creates the `DCTEncode` JPEG compression filter for the PostScript interpreter.

## Key Functions
- `zDCTE()` allocates IJG compression data, initializes `stream_DCT_state`, reads encoder parameters, adjusts template buffer sizes, and opens a write filter.

## Important Behavior
- Uses stable, immovable memory for `jpeg_compress_data`.
- Parameter parsing is delegated to `s_DCTE_put_params()`.
- The copied stream template is adjusted so input buffering can hold a full scanline and output buffering can hold marker data.

## Research Notes
Mostly lifecycle and PostScript parameter plumbing for the JPEG stream layer.
