# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runetype.c

This file contains Unicode rune classification and case-conversion tables.

Key behavior:
- Large static tables define lower/upper/title mappings and alphabetic/space ranges.
- `tolowerrune`, `toupperrune`, and `totitlerune` perform case conversion.
- `islowerrune`, `isupperrune`, `isalpharune`, `istitlerune`, and `isspacerune` classify runes.
- Internal `bsearch` searches range tables.

Important details:
- Data-driven Unicode support for the bundled Plan 9 libc.
- Mostly table payload plus small lookup functions near the end.
