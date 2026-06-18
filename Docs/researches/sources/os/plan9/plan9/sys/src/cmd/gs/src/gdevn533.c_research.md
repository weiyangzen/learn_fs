# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevn533.c

Sony NWP-533 laser printer driver.

- User-contributed driver targeting NEWS printer interfaces via `<newsiop/lbp.h>` and printer ioctls.
- Defines the `nwp533` 1-bit printer device using paper constants from the platform header, defaulting to A4.
- `nwp533_open` defaults the output file to `/dev/lbp` when none is supplied.
- `analyze_error` resets and queries printer status, waits for recoverable conditions such as no cartridge, no paper, jam, door open, or test printing, and aborts for severe hardware/toner conditions.
- `nwp533_print_page` stops the printer, seeks to start, writes each padded scan line to the printer file, then starts printing via ioctl.
- `nwp533_close` stops the printer before normal printer-device close.
- Risk notes: platform-specific ioctl paths, blocking sleep/retry loop, typo-laden diagnostics, and several error returns before freeing the scan-line buffer.
