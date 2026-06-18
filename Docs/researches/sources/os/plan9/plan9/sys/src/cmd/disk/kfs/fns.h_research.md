# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/fns.h

This header declares KFS top-level functions and device macros.

Key contents:
- Includes `portfns.h`, which declares most filesystem internals.
- Declares startup/config helpers: `chaninit`, `confinit`, `fsinit`, `iobufinit`, `startproc`, `syncproc`, `syncall`.
- Declares console/parser helpers such as `cmd_exec`, `nextelem`, `number`, `skipbl`.
- Declares wren device functions.
- Defines compatibility macros: `localfs`, `devgrow`, `nofree`, `isro`.
- Defines device method dispatch macros: `superaddr`, `getraddr`, `devsize`, `devwrite`, `devread`.

Notable detail:
- `isro(d)` is hardcoded to `0` here, so read-only enforcement hooks exist but this KFS build treats devices as writable unless other policy blocks writes.
