# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevos2p.c

## Role

OS/2 printer device for Ghostscript. It prints through OS/2 Presentation Manager/spooler APIs and works only when Ghostscript is loaded by a PM application, not as a text-mode executable.

## Exported Device

- `gs_os2prn_device`, named `os2prn`.

## Main Device State

`gx_device_os2prn` extends a printer device with:

- OS/2 anchor block, printer DC, printer presentation space.
- Queue name and enumerated queue list.
- `newframe` tracking.
- Clip box in pixels.
- Memory DC and memory presentation space for bitmap transfer.

## Open Flow

`os2prn_open`:

1. Verifies caller is a PM application.
2. Gets printer queue list and resolves `OS2QUEUE` or `\\spool\\...` filename.
3. Opens the printer device context.
4. Queries printer resolution, hardcopy caps, page size, margins, and clip box.
5. Creates printer and memory presentation spaces.
6. Chooses 1-bit or 24-bit depth based on printer caps unless `BitsPerPixel` is preset.
7. Starts the spool document.
8. Opens Ghostscript printer buffering with a scratch file that is later deleted.

## Print Flow

`os2prn_print_page`:

- Builds a `BITMAPINFOHEADER2` plus palette for <=8-bit output.
- Allocates a slice buffer limited by `65535 / bmp_raster`.
- Starts new frames after the first page.
- Copies scan lines into bottom-up bitmap slices.
- Uses `GpiDrawBits` to draw DIB data into a memory bitmap.
- Uses `GpiBitBlt` to copy clipped slices to the printer presentation space.

## Parameters

- `os2prn_get_params` exposes `OS2QUEUE`.
- `os2prn_put_params` accepts `OS2QUEUE` and `BitsPerPixel` only before open.
- `os2prn_set_bpp` configures either 24-bit RGB or black-and-white color info and mapping procedures.

## Queue Helpers

- `os2prn_get_queue_list` calls `SplEnumQueue`, allocates enough memory for level-3 queue info, and detects the default queue.
- `os2prn_free_queue_list` releases that allocation.

## Risks and Edge Cases

- Several OS/2 resource allocation failures return without unwinding every already-created resource.
- The print-page path initializes `code` to 0 and does not propagate many OS/2 API return failures after drawing/blitting.
- This is deeply platform-specific and not relevant to Plan 9 runtime behavior except as vendored Ghostscript source.
