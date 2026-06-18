# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpm.c

OS/2 Presentation Manager display driver for Ghostscript. It backs rendering with a BMP bitmap in shared memory or DLL-local memory, then communicates updates to either an outboard `gspmdrv.exe` process, PM GSview, or a DLL callback.

Key behavior:
- Defines `gx_device_pm`, containing regular device state, PM-specific parameters (`BitsPerPixel`, `UpdateInterval`, `GSVIEW`), synchronization handles, process/session ids, shared bitmap memory, committed size, BMP header pointer, and an embedded memory device.
- Exports `gs_os2pm_device`, and conditionally `gs_os2dll_device`, both defaulting to 24-bit color at 96 DPI.
- `pm_open` validates OS/2 mode, creates or opens shared memory/semaphores/queues/mutexes, initializes BMP metadata, sets color depth, allocates the memory-backed bitmap, and starts `gspmdrv.exe` unless GSview or DLL callback mode owns display.
- `pm_get_initial_matrix` uses a bottom-left BMP coordinate convention and pings GSview that drawing has begun.
- `pm_sync_output`, `pm_do_output_page`, and `pm_output_page` signal screen updates, page boundaries, GSview begin/end markers, session foreground selection, and output-page completion.
- `pm_close` signals close to GSview or stops the PM driver session, waits for termination, frees bitmap memory, and closes PM synchronization objects.
- `pm_map_rgb_color` and `pm_map_color_rgb` implement 24-bit BGR-ish packing, an 8-bit dynamic palette, 4-bit PC palette mapping, and monochrome fallback.
- Drawing operations delegate to the embedded memory device and then schedule asynchronous display updates.
- `pm_get_params` and `pm_put_params` expose `UpdateInterval`, `GSVIEW`, and `BitsPerPixel`, while handling size/depth changes without the default close/reopen path.
- `pm_run_gspmdrv` locates and starts the outboard PM display process with a generated id string and termination queue.
- `pm_alloc_bitmap` commits enough shared memory for the BMP header, palette, raster bits, and line pointers, then initializes the embedded memory device over that memory.
- `pm_makepalette`, `pm_update`, `pm_set_bits_per_pixel`, and `pm_palette_size` manage PM palette and Ghostscript color-info setup.
- `pm_write_bmp` is a debug helper that writes the current BMP image to `out.bmp`.

Notable dependencies:
- OS/2 APIs and types from `<os2.h>`, including `DosAllocSharedMem`, semaphores, queues, sessions, and timers.
- Ghostscript device, memory-device, parameter, platform, and PC palette APIs: `gxdevice.h`, `gxdevmem.h`, `gsparam.h`, `gdevpccm.h`, `gp.h`, `gpcheck.h`.
- Shared PM naming/message constants from `gdevpm.h`.
- Optional DLL callback support from `gsdll.h` and `gsdllos2.h`.

Research notes:
- This is platform display plumbing, not filesystem logic, but it is part of the in-scope 9front Ghostscript source tree.
- The driver has several cleanup paths that close or free handles opportunistically; some failure paths close handles that may not have been initialized in all branches.
- `pm_put_params` explicitly says its recovery after failed bitmap reallocation is wrong because other parameters may already have changed.
- The 8-bit palette grows dynamically up to 230 entries to leave colors for PM and other applications.
