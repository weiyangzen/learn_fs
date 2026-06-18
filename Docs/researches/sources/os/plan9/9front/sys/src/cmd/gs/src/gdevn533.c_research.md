# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevn533.c

## Role

Sony NWP-533 printer driver for Ghostscript, contributed by a user.

## Exported Device

- `gs_nwp533_device`, named `nwp533`, 1-bit printer output.
- Defaults to A4 paper if `A4_PAPER` is defined.

## Main Flow

- `nwp533_open` defaults output filename to `/dev/lbp` if none is provided, then opens the printer device.
- `nwp533_print_page` stops the printer, seeks to start, writes padded scan-line data, and starts printing via device ioctls.
- `nwp533_close` sends `LBIOCSTOP` before closing.
- `analyze_error` resets and queries printer status, waits for recoverable conditions such as no paper, jam, or door open, and rejects hardware faults.

## Dependencies

Includes `<sys/ioctl.h>` and `<newsiop/lbp.h>`, making this highly platform/device-specific.

## Risks and Edge Cases

- Several error paths return without freeing the allocated line buffer.
- Error reporting uses `perror` with human-readable status strings, not Ghostscript diagnostics.
- Uses `sleep`, `lseek`, `write`, and raw printer ioctls directly.
