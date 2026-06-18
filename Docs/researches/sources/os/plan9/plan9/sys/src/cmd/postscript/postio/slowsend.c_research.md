# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/slowsend.c

Slow-send fallback for `postio`.

Key responsibilities:
- Provides `slowsend(fd_in)`, a conservative transmission loop for printers or links with unreliable flow control.
- Sends large chunks only when the printer reports `WAITING`.
- Sends small chunks for `BUSY`, `IDLE`, and `PRINTING`.
- Sleeps on `PRINTERERROR`, ignores transient `NOSTATUS`/`UNKNOWN`, and aborts on PostScript errors, flushing, or disconnect.
- Provides a local static `writeblock(num)` that limits each write to at most `num` bytes.

Integration:
- Uses global `postio` send buffer state: `block`, `blocksize`, `head`, `tail`, `line`, `mesg`, and `ttyo`.
- Calls `readblock()`, `getstatus()`, `error()`, and writes directly to `ttyo`.
- Enabled by `postio -S`, which also disables split mode and caps block size in `initialize()`.

Risks and quirks:
- Comments explicitly call it a last-resort workaround.
- It can be very slow and depends on reliable status responses.
- Has a local `writeblock()` with the same conceptual role but different signature from `postio.c`’s `writeblock()`.
