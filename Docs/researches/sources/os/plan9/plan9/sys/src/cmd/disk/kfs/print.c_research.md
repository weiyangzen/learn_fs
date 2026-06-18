# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/print.c

This file implements an older local printf-style formatter.

Key behavior:
- Defines formatter state `Op`-based conversion dispatch through `fmtinstall`, `doprint`, and converter functions.
- Supports base conversions `%c`, `%d`, `%h`, `%l`, `%o`, `%s`, `%u`, `%x`, and `%%`.
- `numbconv` handles signed/unsigned, short/long, width, precision, and bases 8/10/16.
- `strconv` applies width and precision to string output.

Role:
- Portability/compatibility formatting layer for old KFS/Plan 9 code.
- Separate from the Plan 9 `Fmt` system used elsewhere in current files.

Notable detail:
- The file relies on types/macros such as `Op`, `FLONG`, `FSHORT`, and `FUNSIGN` that are expected from the broader historical build environment.
