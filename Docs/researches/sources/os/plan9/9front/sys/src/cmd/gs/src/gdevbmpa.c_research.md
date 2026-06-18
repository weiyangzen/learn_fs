# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbmpa.c

## Purpose
Implements asynchronous BMP output devices as a demonstration of Ghostscript async rendering and command-list rendering.

## Devices
- `bmpamono`
- `bmpasep1`
- `bmpasep8`
- `bmpa16`
- `bmpa256`
- `bmpa16m`
- `bmpa32b`

## Device Structure
Defines `gx_device_async`, extending printer-device fields with:
- `UsePlanarBuffer`
- `buffered_page_exists`
- `file_offset_to_data[4]`

## Main Behavior
- Writer open procedures configure async render procs and start the async writer/render setup with `gdev_prn_async_write_open`.
- Render thread entry calls `gdev_prn_async_render_thread`.
- Output opens the printer stream as positionable so the renderer can seek and update partial pages.
- `bmpa_reader_print_planes` writes BMP headers and bottom-to-top raster data, saving data offsets for later overlays.
- `bmpa_reader_buffer_planes` can seek back into an existing BMP data area, read bands into a buffer device, continue rendering over them, and write updated bands back.
- Supports both ordinary BMP output and separated CMYK plane output.

## Parameters
- `bmpa_get_params` and `bmpa_put_params` delegate to planar printer parameter helpers and expose/control `UsePlanarBuffer`.
- `bmpa_get_hardware_params` publishes a test-only `TestValue`.

## Memory/Banding
- `bmpa_get_space_params` computes band dimensions and buffer sizes for async command-list rendering.
- The comments provide an extensive explanation of writer/render buffer partitioning, tile cache size, command buffer sizing, and async reader/writer matching.

## Dependencies
Uses async printer infrastructure from `gdevprna.h`, BMP helpers, PCL/planar printer helpers, synchronization/thread support, and command-list rendering APIs.

## Notes
- The source explicitly warns that multi-page BMP output is technically possible but most BMP consumers display only the first page.
- This file is both a functional driver and a tutorial-style example of async rendering.
