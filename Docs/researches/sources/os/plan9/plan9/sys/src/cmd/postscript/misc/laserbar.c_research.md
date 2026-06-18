# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/laserbar.c

Code 39 barcode generator for PostScript output.

Key responsibilities:
- Maps supported characters to Code 39 wide/narrow bar patterns.
- Parses rotation, offsets, scaling, label, newpath, and showpage options.
- Emits PostScript definitions for wide bars, narrow bars, and labels.
- Wraps the requested string with start/stop `*`.

Important behavior:
- Lowercase letters are accepted and labeled uppercase.
- Offsets are specified in inches and converted to points.
- Unsupported characters are skipped.

Notable risks:
- Uses global `right` state reset after each barcode.
- Command-line build depends on `MAIN` being defined in this file.
