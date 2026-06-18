# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevice.c

This is the central Ghostscript library implementation for device and page control.

Major areas:
- Device finalization, GC pointer enumeration/relocation, and structure descriptors.
- Page operations: `gs_flushpage`, `gs_copypage`, `gs_output_page`, and `gx_finish_output_page`.
- Scanline copying through `get_bits`.
- Current-device access and device lookup by index from the compiled library device list.
- Device cloning via `gs_copydevice2` and `gs_copydevice`.
- Device opening, closing, and procedure vector initialization.
- Graphics-state device switching through `gs_setdevice`, `gs_setdevice_no_erase`, and `gs_setdevice_no_init`.
- Null-device creation and selection.
- Page geometry helpers for width/height, resolution, media size, margins, tray orientation, and raster size.
- Forward-device color parameter/procedure copying.
- Output filename parsing and opening/closing output streams.

The output filename parser recognizes:
- Empty names.
- `-` for stdout.
- `|command` for pipe output.
- `%` page-number format strings, validating width/precision/type and rejecting multiple format specs.
- Ghostscript IODevices such as `%stdout`.

Device cloning is deliberately conservative. The comments warn that `keep_open` and raw device copying are dangerous because device structs can contain internal pointers or self-pointers. Device-specific `finish_copydevice` hooks are expected to reject unsafe copies.

This file is a core integration hub for graphics state, memory management, IO devices, printer output, command-list devices, and color mapping.
