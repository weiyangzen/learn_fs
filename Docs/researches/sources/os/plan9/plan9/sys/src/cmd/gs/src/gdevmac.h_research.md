# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.h

Defines the shared declarations and data structures for the legacy MacOS PICT device. It includes Mac Toolbox headers, Ghostscript device/font headers, and `gdevmacpictop.h`.

The central type is `gx_device_macos`, extending `gx_device_common` with output filename/file state, `PicHandle`, current PICT write pointer, page-reset state, external font flag, and cached font state.

It declares all Mac device procedures used by `gdevmac.c`, including drawing, page handling, parameter handling, alpha copy, and xfont lookup support. It also defines the `mac_xfont` structure used by `gdevmacxf.c`.

The `CheckMem` macro grows the PICT handle while preserving the current write offset. `ResetPage` clears page-output state and resets PICT position/font cache before further drawing after an output page.

The header also defines default 8.5x11 page/device geometry at 72 DPI and exports `gsdll_get_pict` for external callers.
