# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/data.c

Static error and tag-name tables for cwfs.

Key responsibilities:
- Defines `errstr9p[MAXERR]`, mapping internal error codes to human-readable 9P/server messages.
- Defines `wormscode[0x80]`, mapping optical/SCSI WORM sense-like codes to text.
- Defines `tagnames[]`, mapping block tag constants to diagnostic names.

Important interactions:
- `errstr9p` is used by `console.c`/protocol code for chat/error output.
- `tagnames` is used by diagnostics in `iobuf.c`, `cw.c`, and `sub.c`.

Research notes:
- Some error strings are operationally specific to 9P1-era behavior (`wstat`, `attach`, `walk`, etc.).
- `tagnames` is conditional on `COMPAT32` for higher indirect tags.
