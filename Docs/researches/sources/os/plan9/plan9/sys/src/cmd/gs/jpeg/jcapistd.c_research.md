# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapistd.c

Standard public compressor API implementation for normal full-image compression.

Key behavior:
- `jpeg_start_compress` requires `CSTATE_START`, optionally unsuppresses all tables, resets error/destination modules, initializes the full compression master, prepares the first pass, sets `next_scanline` to zero, and transitions to `CSTATE_SCANNING` or `CSTATE_RAW_OK`.
- `jpeg_write_scanlines` requires scanline state, warns on excess calls, updates progress monitor state, lets the master perform delayed pass startup on first data write, clamps input rows to the remaining image height, calls the main controller’s `process_data`, advances `next_scanline`, and returns rows consumed.
- `jpeg_write_raw_data` requires raw-data state, warns on excess calls, updates progress, performs delayed startup, requires at least one full iMCU row, calls the coefficient controller directly, handles suspension by returning zero, advances `next_scanline`, and returns the iMCU-row height.

Dependencies:
- Internal IJG compressor modules via `jpeglib.h`: destination manager, master controller, main controller, coefficient controller, progress monitor, and table suppression routine from `jcapimin.c`.

Research notes:
- This file is separated from `jcapimin.c` so transcoding-only programs need not link the whole compressor.
- Delayed pass startup is what allows applications to write special markers after `jpeg_start_compress` and before image data.
- Raw-data callers must supply exactly enough component data for an iMCU row contract.
