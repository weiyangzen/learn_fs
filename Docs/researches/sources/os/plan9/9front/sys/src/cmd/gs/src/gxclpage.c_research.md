# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.c

Implements saved-page support for Ghostscript printer devices using command-list banding.

Key behavior:
- `gdev_prn_save_page` verifies the printer is banding, finalizes the current clist page, closes command/block files without deleting them, snapshots core device data and page metadata, records copy count, and reopens the printer clist device for continued use.
- Saves the device name and checks it fits the fixed saved-page name buffer.
- Clears saved `cfile` and `bfile` pointers in page info so the saved object carries file names/metadata rather than live handles.
- `gdev_prn_render_pages` validates that all saved pages are compatible with the target rendering device by device name, color info, Y offset, buffer space, band width, and band height.
- Sets the clist reader’s placed-page array and count, then calls the target device’s normal `output_page`.
- Deletes the saved pages’ temporary command/block files after rendering.

Dependencies:
- Uses printer device definitions from `gdevprn.h`, clist internals from `gxcldev.h`, and saved-page declarations from `gxclpage.h`.
- Relies on command-list file functions such as `clist_end_page`, `clist_fclose`, and `clist_unlink`.

Research notes:
- Saved page rendering currently disallows nonzero Y offsets and requires consistent band height across all pages.
- Compatibility checking is conservative but incomplete for full color representation, as noted in the comments.
