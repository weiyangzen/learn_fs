# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarcat.c

`tarcat` concatenates multiple tar archives into one valid tar archive on stdout.

Behavior:
- Reads each input archive from stdin or named files.
- For each member, `catenate` copies the header with `writetar` and copies payload blocks with `passtar`.
- It deliberately omits the zero end blocks from input archives and emits a fresh end marker through `closeout`.

CLI:
- Supports `-d` for debug logging.
- Usage: `tarcat [-d] [file]...`.

Dependencies:
- `tar.h` and `tarsub.c` for header parsing, checksum validation, block copying, and final zero blocks.

Notable issue:
- The debug message argument order appears reversed: `fprint(2, "%s: reading %s\n", inname, argv0);` prints input name as the command prefix.
