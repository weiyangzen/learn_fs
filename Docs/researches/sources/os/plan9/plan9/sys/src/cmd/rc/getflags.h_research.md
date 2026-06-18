# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/getflags.h

Tiny shared header for rc flag parsing.

Defines:
- `NFLAG 128`;
- global `flag[NFLAG]`;
- `cmdname`;
- sentinel `flagset`;
- prototype for `getflags()`.

Risk/notes:
- The `flag` table assumes ASCII-ish single-byte option characters below 128.
