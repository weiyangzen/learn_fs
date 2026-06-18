# File Research: sources/os/plan9/9front/sys/src/cmd/chmod.c

Plan 9 `chmod` command implementation.

Key behavior:
- Accepts octal modes or symbolic mode specs of the form `[who]op[rwxalt]`.
- `parsemode` supports `u`, `g`, `o`, `a`; operators `+`, `-`, `=`; permissions `r`, `w`, `x`; and Plan 9 flags append (`a`), exclusive (`l`), temp (`t`).
- For octal input, masks read/write/execute bits for all classes.
- For each target, reads current `Dir`, computes `(old & ~mask) | (mode & mask)`, and applies with `dirwstat`.

Dependencies:
- Includes Plan 9 `<u.h>` and `<libc.h>`.
- Uses Plan 9 mode bits `DMREAD`, `DMWRITE`, `DMEXEC`, `DMAPPEND`, `DMEXCL`, and `DMTMP`.

Research notes:
- Symbolic `-` works by masking selected bits and complementing requested mode bits.
