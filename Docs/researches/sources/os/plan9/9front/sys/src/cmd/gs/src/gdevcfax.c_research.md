# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcfax.c

Ghostscript CAPI fax SFF writer. It defines the `cfax` fax device using fax printer parameters, CCITT fax encoding, and custom SFF document/page framing.

Key behavior:
- `gs_cfax_device` is declared through `FAX_DEVICE_BODY` with `cfax_print_page`.
- `cfax_doc_hdr`, `cfax_page_hdr`, and `cfax_doc_end` emit SFF container markers and little-endian numeric fields.
- `cfax_print_page` initializes a `stream_CFE_state` for 1-D Group 3-style encoding with byte alignment and low-order first bit order.
- `cfax_stream_print_page_width` copies every scanline, pads width-adjusted rows, runs the stream encoder per line, and writes SFF line records using short or long length forms.
- `cfax_prn_close` appends the SFF end-of-document marker before normal printer close.

Notable dependencies:
- Ghostscript printer/fax APIs: `gdevprn.h`, `gdevfax.h`.
- Stream compression interfaces: `strimpl.h`, `scfx.h`.

Research notes:
- The code supports multipage SFF output by detecting new files for the document header and using a special close hook for document termination.
- A narrow resource risk exists in `cfax_stream_print_page_width`: if encoder init fails inside the line loop, the function returns immediately rather than going through the cleanup label, so temporary buffers may leak on that error path.
