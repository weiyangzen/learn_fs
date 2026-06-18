# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.c

## Purpose
Implements saved-page management for banding printer devices.

## Main Responsibilities
- Saves the current banded page into a `gx_saved_page`.
- Renders an array of saved pages at specified offsets.
- Validates saved-page compatibility with the rendering printer device.
- Deletes temporary clist files after rendering placed pages.

## Key Implementation Details
- `gdev_prn_save_page` requires banding (`pdev->buffer_space` nonzero).
- Saving a page ends the clist page, closes command/block files without deleting them, copies device metadata, and reopens the printer device.
- `gdev_prn_render_pages` checks device name, color info, Y offset, buffer space, band width, and band height compatibility.
- Rendering works by setting placed-page data into the clist reader and invoking the printer’s `output_page`.

## Limitations
- Y translation is currently rejected; only X offsets are allowed.
- Saved pages must come from the same device type and compatible band parameters.
- Color representation checking is only partial.

## Dependencies
- `gdevprn.h` for printer device type.
- `gxcldev.h` for clist internals.
- `gxclpage.h` for saved-page declarations.

## Research Notes
This file lets command-list pages become composable page objects. It is separate from normal clist page finalization because it preserves temporary band files for later rendering.
