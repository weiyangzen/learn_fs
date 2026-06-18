# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbmpa.c

Async-rendering demonstration version of the BMP output drivers. It mirrors the synchronous BMP devices but uses Ghostscript's async printer/clist machinery to overlap interpretation and rendering.

Key behavior:
- Defines `gx_device_async`, extending printer device state with `UsePlanarBuffer`, `buffered_page_exists`, and per-plane file offsets.
- Defines async BMP devices for mono, separated CMYK 1/8-bit, 4-bit, 8-bit, 24-bit, and 32-bit CMYK-like output.
- `bmpa_open_writer` installs async render procedures, parameter hooks, hardware-param hook, output-page hook, space-parameter hook, and optional planar buffering, then opens with `gdev_prn_async_write_open`.
- `bmpa_reader_start_render_thread` launches the render thread through `gp_create_thread`.
- `bmpa_reader_output_page` opens the output as positionable so the renderer can seek back and update already written BMP data.
- `bmpa_reader_print_planes` writes headers, records the data offset, and writes rendered rows bottom-to-top for either normal or separated-plane output.
- `bmpa_reader_buffer_planes` reopens existing BMP raster data, reads bands back into a buffer device, renders additional clist content over it, and writes updated bands back in place.
- `bmpa_get_space_params` computes band buffer sizes for async writer/reader compatibility, then forces buffer and band-buffer space to match.
- `bmpa_get_params`/`bmpa_put_params` expose planar-buffer behavior through printer parameter helpers.
- `bmpa_get_hardware_params` returns a test-only `TestValue`.

Notable dependencies:
- Async printer/clist APIs: `gdevprna.h`, `gdevppla.h`, `gpsync.h`.
- BMP helpers: `gdevbmp.h`.
- PC color mapping helpers: `gdevpccm.h`.

Research notes:
- The file is explicitly a demo of async rendering, not just another BMP writer.
- Positionable output is required; non-seekable streams would not support the buffered-page overlay path.
- The comments explain Ghostscript clist memory sizing in unusual detail and are a useful reference for async printer driver construction.
- `SINGLE_PAGE` can be enabled to discard all but the first page, but is disabled because Ghostscript may write multiple BMP streams even though many viewers only process the first.
