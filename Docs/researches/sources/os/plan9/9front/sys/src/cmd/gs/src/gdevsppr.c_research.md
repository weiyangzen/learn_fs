# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsppr.c

Ghostscript printer driver for Sun SPARCprinter / lpviio interface.

Key behavior:
- Defines the `sparc` monochrome printer device at 400x400 DPI.
- Sets page margins during open based on paper height, distinguishing A4-like vs letter-like pages.
- Retrieves and updates the printer page descriptor through `LPVIIOC_GETPAGE` and `LPVIIOC_SETPAGE`.
- Sets bitmap width, page width, page length, and 300/400 DPI resolution in `lpvi_page`.
- Copies the entire rendered bitmap into an output buffer and writes it to the printer file descriptor.
- On short write/error, queries printer status with `LPVIIOC_GETERR`.
- Distinguishes warnings, fatal engine errors, driver/interface errors, and unknown status.
- Retries warning conditions after sleeping five seconds.
- Converts lpvi error codes to strings with a static table and fallback buffer.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Sun printer driver interface: `unbdev/lpviio.h`.

Research notes:
- The driver intentionally avoids asynchronous I/O.
- `warning` is a global state flag used to print an “OK” message after recovery.
- The write buffer is not freed on several early error returns inside the retry loop.
