# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/date.c

This file parses IMAP and mail date formats for the IMAP daemon.

Key behavior:
- `imap4date` parses `DD-Mon-YYYY` style IMAP dates.
- `imap4datetime` parses IMAP internal datetime variants and returns seconds or `~0` on failure/out-of-range.
- `date2tm` parses common RFC/mail date variants for FETCH envelope/internal date output.

Integration and risks:
- Shared by search/fetch/status code through declarations in `fns.h`.
