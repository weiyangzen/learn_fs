# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfdctd.c

## Purpose
Creates the `DCTDecode` JPEG decompression filter for the PostScript interpreter.

## Key Functions
- `zDCTD()` allocates IJG decompression data, initializes `stream_DCT_state`, reads dictionary parameters, creates the JPEG decompressor, and wraps it in a read filter.

## Important Behavior
- Uses immovable allocation for `jpeg_decompress_data` because libjpeg stores internal pointers.
- Parameter parsing is delegated to `s_DCTD_put_params()` from `sddparam.c`.
- Error exits destroy the JPEG state and free the auxiliary structure if the filter stream was not successfully registered.
- If the top operand is not a dictionary, defaults are used.

## Research Notes
This file is thin interpreter glue around the JPEG stream implementation in `sjpeg`/`sdct`.
