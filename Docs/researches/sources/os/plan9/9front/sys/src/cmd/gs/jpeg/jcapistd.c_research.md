# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcapistd.c

Standard public compression API for full pixel-to-JPEG compression.

Key points:
- `jpeg_start_compress` requires `CSTATE_START`, optionally unsuppresses all tables, resets error/destination managers, initializes the full compressor module graph via `jinit_compress_master`, prepares the first pass, sets `next_scanline = 0`, and enters either `CSTATE_RAW_OK` or `CSTATE_SCANNING`.
- `jpeg_write_scanlines` validates scanning state, warns on excess calls, updates progress, triggers delayed frame/scan marker output on the first call, caps input at remaining image height, and delegates to the main controller.
- `jpeg_write_raw_data` is the raw-downsampled-data entry point; it validates raw state, requires at least one iMCU row, triggers delayed headers, calls the coefficient controller directly, and advances `next_scanline` by one iMCU row.

Dependencies and interactions:
- Pulling in this file intentionally links the full compressor, unlike the smaller transcoding API path.
- Uses master, main, coefficient, progress, and destination module contracts initialized by `jcinit.c`.

Risk notes:
- Raw data writes must provide exactly compressor-shaped component planes with at least one full iMCU row.
- Extra scanlines in the final valid call are silently ignored, but calls after the image is complete only warn and return no useful progress.
- Suspension is handled by returning fewer rows, so callers must honor returned row counts.
