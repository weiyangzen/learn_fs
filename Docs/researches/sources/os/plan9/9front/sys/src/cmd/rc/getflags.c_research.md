# File Research: sources/os/plan9/9front/sys/src/cmd/rc/getflags.c

Small command-line flag parser used by `rc`. It scans bundled single-letter options, supports fixed argument counts through a compact flag specification, records values in global `flag[NFLAG]`, and stops at the first non-option when requested.

It mutates `argv` in place, moving flag arguments toward the end and returning the remaining argc. Duplicate flags, unknown flags, bad flag syntax, and too few arguments are recorded for `usage()`.

`usage()` prints direct low-level errors via `Write(2, ...)`, sets shell status to `bad flags`, then exits.
