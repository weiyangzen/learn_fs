# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dwimg.c

Purpose: Win32 image display window implementation for Ghostscript’s display device and graphical trace window.

Major responsibilities:
- Maintains a process-global linked list of `IMAGE` objects keyed by Ghostscript handle/device.
- Creates and destroys image windows.
- Converts Ghostscript display formats to Windows DIB-compatible formats.
- Manages palettes, clipboard export, scroll bars, repainting, drag/drop forwarding, and DeviceN/separation menu controls.
- Supports single-thread and multi-thread modes through per-image mutexes.

Key functions:
- Main-thread image management: `image_find`, `image_new`, `image_delete`, `image_size`, `image_separation`.
- GUI-thread lifecycle: `image_open`, `image_close`, `image_sync`, `image_page`, `image_poll`, `image_updatesize`.
- Color conversion: 16-bit RGB/BGR 555/565 converters, CMYK 4-bit/32-bit conversion, DeviceN conversion, `image_convert_line`.
- Clipboard: `copy_dib`.
- Rendering: `WndImg2Proc`, `draw`.

Notable behavior:
- Supports native, gray, RGB, CMYK, and separation display formats from `gdevdsp.h`.
- For CMYK/DeviceN, adds system-menu entries for visible separations and optional gray display when one component is visible.
- Saves/restores window positions via `win_get_reg_value`/`win_set_reg_value`.
- Uses `SetDIBitsToDevice`, splitting transfers because old Windows limits large DIB transfers.

Risks/bugs observed:
- In `create_window`, comparisons like `if (lb.lbColor = RGB(...))` are assignments, so the intended color checks are not actually comparisons.
- In `image_4CMYK_to_24BGR`, `if (i & 0)` is always false, so odd-pixel nibble selection appears broken.
- Uses old `SetWindowLong`/`GetWindowLong` casts to `LONG`, not pointer-width safe.
- Fixed-size path/title buffers and many unchecked string operations.
- Clipboard path leaks the global allocation if `GlobalLock` fails after `GlobalAlloc`.

Filesystem relevance: None directly. It is Win32 UI/rendering code.
