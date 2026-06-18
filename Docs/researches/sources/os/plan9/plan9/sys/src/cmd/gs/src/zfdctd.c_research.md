# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfdctd.c

## Purpose
Creates the `DCTDecode` JPEG decompression filter for the PostScript interpreter.

## Key Functions
- `zDCTD()` allocates IJG decompression data, initializes `stream_DCT_state`, reads dictionary parameters, creates the JPEG decompressor, and wraps it in a read filter.

## Important Behavior
- Uses immovable allocation for `jpeg_decompress_data`.
- Parameter parsing is delegated to `s_DCTD_put_params()`.
- Error exits destroy the JPEG state and free auxiliary data if filter creation did not complete.

## Research Notes
This file is thin interpreter glue around the JPEG stream implementation.
