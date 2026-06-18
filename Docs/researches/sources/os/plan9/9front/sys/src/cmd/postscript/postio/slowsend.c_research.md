# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/slowsend.c

`slowsend.c` implements the optional slow transmission path for `postio`, enabled by `-S`.

Behavior:
- `slowsend(fd_in)` loops over `readblock(fd_in)` and checks printer status before writing.
- It writes a full block only when the printer reports `WAITING`.
- For `BUSY`, `IDLE`, and `PRINTING`, it writes only 30 bytes.
- For `NOSTATUS` and `UNKNOWN`, it sends nothing.
- For `PRINTERERROR`, it sleeps for 30 seconds.
- For `ERROR`, `FLUSHING`, and `DISCONNECT`, it reports fatal errors.
- Local static `writeblock(num)` caps writes to `num` bytes and advances shared `head`.

Shared state:
- Uses globals from `postio.c`: `block`, `blocksize`, `head`, `tail`, `line`, `mesg`, and `ttyo`.
- Calls `readblock()`, `getstatus()`, and `error()` from the main postio implementation.

Purpose:
- It is a fallback for printers or Datakit connections with unreliable flow control.
- Comments warn it is slow, single-process only, and disables much of the newer `postio` behavior.

Risk:
- It defines a local `writeblock()` name that intentionally differs from `postio.c`’s no-argument `writeblock()` in old C style; this is fragile with modern prototypes but works in the legacy build model.
