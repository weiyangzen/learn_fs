# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/strparse.c

Small destructive whitespace parser for 9nfs configuration lines.

Key responsibilities:
- Splits a mutable string into whitespace-delimited fields.
- Stops at NUL or the global comment character `strcomment`, default `#`.
- Writes NUL terminators in-place between fields.
- Always terminates the argv array with nil.

Dependencies:
- Uses Plan 9 `<u.h>` and `<libc.h>` only.

Notable risks:
- No quoting or escaping is supported.
- Input must be mutable because separators are overwritten.
