# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdfax.c

Defines DigiBoard DigiFAX low- and high-resolution fax devices.

The file declares `gx_device_dfax`, adding a page counter and image width field to printer-device state. It registers `gs_dfaxlow_device` at 204 x 98 dpi and `gs_dfaxhigh_device` at 204 x 196 dpi. Both share `dfax_prn_open` and `dfax_print_page`.

`dfax_prn_open` resets `pageno` and delegates setup to `gdev_fax_open`. `dfax_print_page` initializes CCITT fax encoding state with EOL and byte alignment enabled, writes a DigiFAX-specific header, emits the fax page via `gdev_fax_print_page`, then seeks back to update the total page count in the file header.

Dependencies are Ghostscript printer/fax infrastructure: `gdevprn.h`, `scfx.h`, `gdevfax.h`, and `gdevtfax.h`.

Risks: the format relies on seekable output because it rewrites the page count at offset 24. The static header is mutated per page. There is no explicit checking of `fseek`/`fwrite` failures.
