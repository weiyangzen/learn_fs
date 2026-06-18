# File Research: sources/os/plan9/plan9/sys/src/9/port/mkrootall

Purpose: rc helper that embeds multiple boot files as assembly data.

Key logic:
- Arguments are repeated triples: `name cname file`.
- Validates argument count is a multiple of three.
- Copies each file to a temp file, strips executables except `venti`, and emits assembly with `aux/data2s cname`.
- Removes temp file on exit.

Dependencies and integration:
- Used by `mkbootrules` to build `$CONF.root.s`.

Risks and notes:
- Does not emit the boot link table; `mkrootc` handles C registration.
