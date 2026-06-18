# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpm.c

This file implements the OS/2 Presentation Manager display device for Ghostscript. Despite being in the Plan 9 source tree copy, it is OS/2-specific display integration, not Plan 9 code.

The file defines `gx_device_pm`, which embeds Ghostscript device state, PM-specific control fields, and a `gx_device_memory` backing device. The PM-specific fields include `BitsPerPixel`, `UpdateInterval`, `GSVIEW`, `dll`, palette size, update timer, shared-memory bitmap pointer, semaphores, mutexes, queues, session IDs, process IDs, and a `BITMAPINFO2` header.

Two devices are defined: `gs_os2pm_device` for the outboard PM driver model and, under `__DLL__`, `gs_os2dll_device` for DLL embedding. `pm_open` creates or opens the necessary OS/2 shared memory and synchronization objects. In non-DLL mode it can either cooperate with PM GSview via pre-existing queue/semaphore names or start `gspmdrv.exe` as a child PM session using `DosStartSession`. It allocates a large shared bitmap region, commits pages on demand, initializes BMP header fields, palette data, and the Ghostscript memory device.

Rendering operations (`pm_fill_rectangle`, `pm_copy_mono`, `pm_copy_color`) delegate to the embedded memory device, then call `pm_update`, which either posts a timer/event or sends queue messages so the display process refreshes. `pm_sync_output`, `pm_output_page`, and `pm_close` coordinate page display, foregrounding the PM session, GSview begin/end/page events, and cleanup.

Color support is parameterized by `BitsPerPixel` values 1, 4, 8, and 24. `pm_set_bits_per_pixel` updates Ghostscript color info and encode/decode procedures; `pm_makepalette` builds OS/2 BMP palettes; 8-bit mode dynamically adds palette colors until reserving entries for PM and other apps.

`pm_get_params`/`pm_put_params` expose `UpdateInterval`, `GSVIEW`, and `BitsPerPixel`, resizing/reinitializing the bitmap while holding the bitmap mutex if dimensions or depth change. Debug-only `pm_write_bmp` can dump `out.bmp`.

Filesystem relevance: limited to file/process interfaces. The driver uses OS/2 shared memory, queues, semaphores, session control, and optionally writes a BMP for testing, but does not implement filesystem logic.
