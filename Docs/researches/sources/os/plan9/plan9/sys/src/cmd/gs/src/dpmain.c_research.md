# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dpmain.c

## Purpose

`dpmain.c` is the OS/2 Ghostscript DLL loader and display bridge for a console-mode application. It dynamically loads `GSDLL2.DLL`, resolves the Ghostscript API, and exposes a display callback backed by shared memory and a separate Presentation Manager driver process, `gspmdrv.exe`.

## Main Components

- `GSDLL` stores the loaded DLL module handle and resolved function pointers for revision, instance lifecycle, stdio, display callback, initialization, execution, and exit.
- `gs_load_dll` locates and loads the DLL, tries executable-relative fallback paths, resolves symbols, and checks `GS_REVISION`.
- `IMAGE` tracks one OS/2 display session: shared bitmap memory, semaphores, mutex, queue, PM session/process IDs, image dimensions, raster format, and linked-list state.
- `run_gspmdrv` starts the PM display process with an ID used to share semaphore and memory names.
- `image_color` and `image_palette_size` synthesize palettes for native and grayscale display formats.
- Display callbacks implement open, preclose, close, presize, size, sync, page, update, memory allocation, and memory free.
- `main` determines display depth, injects `-dDisplayFormat=...`, creates a Ghostscript instance, runs startup PostScript, exits, unloads the DLL, and maps Ghostscript result codes to process exit status.

## Display / IPC Flow

1. `display_open` allows only one image window, creates named event/mutex semaphores, allocates up to 13 MiB shared memory, commits an initial page, and writes an empty `BITMAPINFO2`.
2. `display_presize` validates supported display formats and locks the bitmap mutex before resize.
3. `display_size` writes the bitmap header and optional palette, then releases the mutex.
4. `display_memalloc` does not allocate fresh memory; it commits more of the preallocated shared segment and returns a pointer after the BMP header/palette.
5. `display_sync` lazily starts `gspmdrv.exe` once dimensions are known and posts the update event semaphore.
6. `display_preclose` stops the PM session, waits on the termination queue, and closes semaphores.
7. `display_close` frees shared memory.

## Filesystem Relevance

No filesystem implementation is present. The file uses OS/2 module-path discovery and process launching to find `GSDLL2.DLL` and `gspmdrv.exe`, but its main role is display IPC for Ghostscript.

## Risks / Portability Notes

- Multiple image windows are deliberately disabled due to OS/2 child-session termination-queue behavior.
- Shared memory is preallocated large and committed in chunks; failure paths must avoid leaking semaphores or memory.
- The code depends on OS/2 APIs, named semaphores, queues, and Presentation Manager behavior.
