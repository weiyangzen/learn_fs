# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2receive.c

Receives fax pages from a Class 2 modem and writes them into spool files.

Key behavior:
- `page()` sends `AT+FDR`, waits for `CONNECT`, creates the page file, sends DC2, and reads page data until DLE ETX.
- DLE escaping is handled by treating doubled DLE as data and DLE ETX as page termination.
- Buffered page data is written to `m->pagefd`.
- After page data, waits for `OK` or `ERROR`.
- `receive()` loops pages, validates `FPTS`/`FET`/`FHNG`, retries failed pages, and handles multi-document sessions.
- `faxreceive()` initializes fax modem state and assumes the call has already been answered with `+FCON`.

Important implementation details:
- Page files are named and headered by `createfaxfile()`.
- New documents are logged but remain queued due to a noted limitation.
- Hangup code zero is success; other hangup codes become attention errors.

Risks and invariants:
- The page receive buffer is 100 KB and flushed when full.
- Cleanup of failed document pages is commented out.
