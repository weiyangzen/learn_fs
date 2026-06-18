# File Research: sources/os/plan9/9front/sys/src/cmd/basename.c

This is a compact implementation of `basename` with an added `-d` dirname-like mode.

Behavior:
- `basename string [suffix]` prints the final path component.
- If `suffix` is supplied and matches the end of the basename, it is stripped in place.
- `basename -d string` prints the directory portion before the last slash, or `.` if there is no slash.

Notable implementation details:
- Uses `utfrrune` to find the final `/`.
- Mutates `argv[1]` or the local basename buffer directly by inserting NULs.

Risks and caveats:
- Assumes argument strings are mutable, as is common in this Plan 9 C environment.
