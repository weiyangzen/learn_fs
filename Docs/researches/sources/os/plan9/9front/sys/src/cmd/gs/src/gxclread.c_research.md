# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclread.c

Command-list band reader and rendering bridge.

Key behavior:
- Defines a `stream_band_read_state` stream filter that scans a band index file and reads only command runs overlapping the requested band range.
- `s_band_read_process` alternates between reading command bytes from the command file and scanning `cmd_block` records from the band file.
- `clist_setup_params` replays initial clist parameters for async rendering setup.
- `clist_get_bits_rectangle` rasterizes requested lines into a buffer device and then copies the requested rectangle to caller-provided `get_bits` buffers.
- Selects plane-specific rendering when possible, but falls back to full-pixel rendering if multiple planes are requested or RasterOp requires slow full-color handling.
- `clist_rasterize_lines` renders one band at a time, sets up the memory/buffer device over the reader’s scratch storage, and caches current rasterized band bounds.
- `clist_render_rectangle` renders one rectangle across one or more bands, including saved/placed pages, and clears the destination buffer when requested.
- `clist_playback_file_bands` opens saved page band/command files if needed, wraps the band-read filter in a stream, and calls `clist_playback_band`.

Notable dependencies:
- `gxclrast.c` for actual command playback.
- Printer/buffer-device helpers such as `gdev_prn_colors_used` and `gdev_create_buf_device`.
- Clist file abstraction and band-page metadata.

Research notes:
- This file separates band selection and buffering from opcode interpretation.
- It supports incremental `get_bits_rectangle` delivery when requested lines cross band boundaries.
- It includes a design note that printer-device dependencies are undesirable but currently required for colors-used and buffer-device creation.
