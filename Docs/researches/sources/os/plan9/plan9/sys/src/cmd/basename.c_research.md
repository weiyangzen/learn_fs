# File Research: sources/os/plan9/plan9/sys/src/cmd/basename.c

Plan 9 `basename` implementation.

Behavior:

- Usage: `basename [-d] string [suffix]`.
- Without `-d`, prints the final path component after the last `/`.
- With optional suffix, strips that suffix from the basename if present.
- With `-d`, prints the directory portion before the last `/`, or `.` if none exists.

Uses Plan 9 UTF-aware `utfrrune()` to find the final slash.
