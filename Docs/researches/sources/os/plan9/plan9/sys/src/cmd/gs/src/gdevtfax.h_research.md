# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.h

Declares the shared TIFF/Fax page writer entry point used by fax-capable Ghostscript drivers.

Key behavior:
- Provides the prototype for `gdev_fax_print_page_stripped`, which writes a fax-encoded printer page using a `stream_CFE_state` and a requested rows-per-strip value.

Dependencies:
- Assumes callers have visible definitions for `gx_device_printer`, `FILE`, and `stream_CFE_state` from the surrounding Ghostscript headers.

Research notes:
- This is a minimal interface header; the behavior and validation live in `gdevtfax.c`.
