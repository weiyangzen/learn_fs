# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdfax.c

Ghostscript DigiBoard DigiFAX output device.

Key behavior:
- Defines `dfaxlow` and `dfaxhigh` devices at 204 DPI horizontal resolution and low/high vertical fax resolutions.
- Extends the printer device with a page counter and image-width field.
- `dfax_prn_open` resets the page counter and delegates to fax-device open logic.
- `dfax_print_page` configures CCITT fax encoding state with EOL markers and byte alignment.
- Writes a fixed DigiFAX page header, updates page number and resolution bits, appends encoded fax page data via `gdev_fax_print_page`, then seeks back to update the total page count.

Notable dependencies:
- Ghostscript printer/fax APIs: `gdevprn.h`, `gdevfax.h`, `gdevtfax.h`.
- Stream compression interfaces: `strimpl.h`, `scfx.h`.

Research notes:
- The driver is marked as user-maintained legacy code.
- It uses `fseek` to patch the page count after page output, so output streams must be seekable for correct headers.
- Header bytes are stored in a static buffer and modified per page.
