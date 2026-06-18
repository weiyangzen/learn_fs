# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwimg.c

## Role
Win32 image window implementation for Ghostscript's display device callback. It creates and manages raster display windows, scrolling, clipboard export, separations menus, palettes, and pixel-format conversion.

## Contents
- Maintains global linked list `first_image` of `IMAGE` objects keyed by Ghostscript handle/device.
- Main-thread APIs create/find/delete image records and update bitmap metadata from Ghostscript display callbacks.
- GUI-thread APIs register/create/destroy image windows, redraw/sync pages, manage periodic update timers, and update scrollbars.
- Converts Ghostscript display formats to Windows DIB output: native indexed/16-bit/32-bit, gray, RGB, CMYK, and DeviceN separations.
- Builds palettes and clipboard DIB data, avoiding 16/32-bit clipboard formats for older viewers.
- Provides system menu commands for copying to clipboard, toggling DeviceN gray preview, and toggling individual separations.
- Window procedure handles creation, sizing, scrolling, keyboard forwarding, character forwarding to text/console, timer updates, painting, drag-and-drop, and persistence of image/tracer window geometry in the Ghostscript registry key.

## Important Interfaces
- From `dwimg.h`: `image_find`, `image_new`, `image_delete`, `image_size`, `image_open`, `image_close`, `image_sync`, `image_page`, `image_poll`, `image_updatesize`.
- Extra implemented function used externally: `image_separation`.
- Internal conversion helpers: `image_convert_line`, 16-bit RGB/BGR converters, CMYK/DeviceN converters, `copy_dib`, `create_palette`, `draw`.
- Window procedure `WndImg2Proc`.

## Dependencies And Coupling
- Includes Win32, Ghostscript API/display headers (`iapi.h`, `gdevdsp.h`), `dwmain.h`, `dwimg.h`, and `dwreg.h`.
- Shares `hwndtext` from `dwmain.h` to forward input to the text window.
- Designed to operate in both single-threaded `dwmain.c` and two-threaded `dwmainc.c`; thread safety depends on `IMAGE::hmutex` when used.
- Uses registry helpers to persist `"Image"` and `"Tracer"` window positions.

## Risks And Notes
- Several fixed-size buffers and legacy Win32 APIs are used.
- Background brush selection uses assignment in conditions (`if (lb.lbColor = RGB(...))`), which means the intended "compare and fall back if white" logic is suspect and always assigns the tested color before entering the branch.
- In `image_4CMYK_to_24BGR`, `if (i & 0)` is always false, so packed nibble handling appears broken for odd pixels.
- `image_separation` allows `comp_num == IMAGE_DEVICEN_MAX`, which is out of bounds for the array of size `IMAGE_DEVICEN_MAX`.
- Paint/clipboard paths assume valid bitmap dimensions and image pointer when called; callers must synchronize around resize/close.

## Filesystem Relevance
Only through drag-and-drop filenames and registry persistence. It is mainly GUI/raster display code.
