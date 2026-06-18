# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dpmain.c

This is the OS/2 Ghostscript DLL loader for a console-compatible executable. It dynamically loads `GSDLL2.DLL`, drives Ghostscript through the DLL API, and uses a separate Presentation Manager helper process, `gspmdrv.exe`, to display rendered pages.

Key responsibilities:
- Loads and unloads the Ghostscript DLL with `DosLoadModule` and `DosFreeModule`.
- Resolves required GS API entry points by name: revision, instance lifecycle, stdio, poll, display callback, init, run string, and exit.
- Verifies that the loaded DLL revision matches the build's `GS_REVISION`.
- Implements stdio callbacks backed by `read`, `fwrite(stdout)`, and `fwrite(stderr)`.
- Determines display depth/capabilities from OS/2 PM/GPI calls and prepends a suitable `-dDisplayFormat=` argument.
- Runs Ghostscript startup with `gsdll.init_with_args`, then executes `systemdict /start get exec\n`, exits the instance, unloads the DLL, and maps Ghostscript return codes to process exit status.

Display architecture:
- `display_open` creates one `IMAGE` record, disallows multiple windows, derives a per-device ID from process/device values, and creates named OS/2 semaphores and shared memory.
- Shared memory is allocated under `\SHAREMEM\...` and initially committed in `MIN_COMMIT` chunks.
- `run_gspmdrv` starts `gspmdrv.exe` as a related child PM session using `DosStartSession`, passing the generated display ID.
- `display_preclose` stops the PM session, waits on its termination queue, and closes synchronization objects.
- `display_close` frees shared bitmap memory.
- `display_presize` validates supported formats and locks the bitmap mutex while size parameters are changing.
- `display_size` writes an OS/2 `BITMAPINFO2` header and optional palette into shared memory.
- `display_memalloc` does not allocate fresh memory; it commits more of the preallocated shared memory and returns a pointer just past the BMP header/palette for Ghostscript's raster.
- `display_sync` lazily starts `gspmdrv.exe` after the image size is known and posts the update semaphore.
- `display_update` is a no-op because the PM helper process owns repaint behavior.

Supported display formats:
- Native or gray 1/4/8-bit indexed formats.
- RGB 8-bit-per-component without alpha.
- The chosen default depends on desktop display depth and palette-manager availability.

Notable implementation details and risks:
- Multiple display windows are intentionally disabled because OS/2 related child sessions and termination queues do not handle the old one-session-per-window design safely.
- The shared memory reservation is fixed at about 13 MB, with chunked commit.
- The code assumes the Ghostscript memory device places the raster immediately at the memory pointer returned by `display_memalloc`.
- There is limited cleanup on some mid-`display_open` failure paths; this is historical sample/platform code.
- `display_memfree` is declared `int` but does not return a value, reflecting old C/platform code style.

Filesystem relevance:
- This file uses OS/2 module loading, process/session creation, queues, semaphores, and shared memory.
- It does not implement filesystem logic, beyond locating/loading DLLs and helper executables via OS/2 APIs.
- Its relevance is platform integration for Ghostscript in the vendored 9front tree.

Research classification: OS/2 Ghostscript DLL loader and Presentation Manager shared-memory display bridge.
