# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.h

## Role
Header for Win32 Ghostscript display image windows.

## Contents
- Defines `IMAGE_DEVICEN`, tracking one color separation/component: usage, visibility, name, CMYK values, and menu state.
- Defines `IMAGE_DEVICEN_MAX` as 8.
- Defines `IMAGE`, the full window/raster state object: Ghostscript handle/device, HWND, brush, raster format/pointer, BITMAPINFOHEADER, palette, DeviceN state, timer state, scroll state, mutex, linked-list pointer, associated text HWND, and saved geometry.
- Declares global `first_image`.
- Declares main-thread and GUI-thread image management APIs.

## Important Interfaces
- Main-thread API: `image_find`, `image_new`, `image_delete`, `image_size`.
- GUI-thread API: `image_open`, `image_close`, `image_sync`, `image_page`, `image_presize`, `image_poll`, `image_updatesize`.

## Dependencies And Coupling
- Requires Win32 types (`HWND`, `HBRUSH`, `BITMAPINFOHEADER`, `HPALETTE`, `HANDLE`).
- Closely paired with `dwimg.c`, `dwmain.c`, `dwmainc.c`, and `dwtrace.c`.

## Risks And Notes
- Header declares `image_presize`, but the implementation in `dwimg.c` does not define it in the read file; callbacks perform presize handling in launcher code.
- The shared `IMAGE` structure is accessed from multiple threads in console mode, so callers must honor the mutex discipline documented in `dwimg.c`.

## Filesystem Relevance
None directly.
