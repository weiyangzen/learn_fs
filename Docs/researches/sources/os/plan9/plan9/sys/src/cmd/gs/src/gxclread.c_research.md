# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclread.c

## Purpose
Implements command-list reading and band rasterization orchestration. It filters command-list files by band range, initializes reader state, renders requested bands into a buffer device, and serves `get_bits_rectangle` requests from rasterized bands.

## Public Surface
- `clist_setup_params(gx_device *dev)`: plays the initial parameter command for async rendering setup.
- `clist_get_bits_rectangle(...)`: rasterizes enough command-list content to return requested pixels.
- `clist_render_rectangle(...)`: renders an arbitrary rectangle of the command list into a caller-supplied device.

## Implementation
- Defines `stream_band_read_state` and `s_band_read_process`, a stream filter that walks the band index file and only emits command runs whose band ranges overlap the requested band range.
- `clist_select_render_plane` chooses a single render plane when possible, but falls back to full-pixel rendering for slow RasterOps.
- `clist_rasterize_lines` lazily renders a band into the command-list reader memory buffer and then rebinds the buffer device to the requested line subset.
- `clist_get_bits_rectangle` supports chunky, planar, bit-planar, selected-plane, pointer, and copy output modes; if a rectangle spans bands, it returns pieces or punts to the default implementation when the request cannot be satisfied incrementally.
- `clist_playback_file_bands` opens saved page command and band files when needed, wraps them in the band-filter stream, calls `clist_playback_band`, and closes only the files it opened.

## Dependencies
Uses Ghostscript clist file APIs, stream APIs, printer buffer-device helpers, rendering planes, memory devices, and `clist_playback_band` from `gxclrast.c`.

## Risks and Notes
- The file comments acknowledge an architectural leak: it includes `gdevprn.h` because some command-list reader services are still printer-device-specific.
- Band filtering depends on consistent `cmd_block` positions in the band index file and command file.
- Multiple selected planes fall back to the default `get_bits_rectangle` path rather than partial clist optimization.

Filesystem relevance: this file opens and reads command-list band files through Ghostscript's clist file abstraction, but its role is rendering-band I/O rather than filesystem implementation.
