# File Research: sources/os/bsd/freebsd-src/sys/sys/sigio.h

Async I/O ownership state for `SIGIO` and `SIGURG`.

Key responsibilities:
- Defines `struct sigio`, recording whether notification targets a process or process group.
- Stores linkage into process/process-group sigio lists, a back-reference pointer location, credentials, and target pgid.
- Defines `sigiolst`.
- Declares `fgetown()`, `fsetown()`, `funsetown()`, and `funsetownlst()`.

Important patterns:
- `sio_myref` allows revocation or clearing of the owning file/socket/device reference.
- Credentials are retained with the registration for later signal delivery checks.
- Process and process-group linkage lets the kernel clean up all async notification state when either disappears.

Research relevance:
- Small but important support type for socket/device asynchronous notification.
