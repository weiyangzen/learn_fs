# File Research: sources/os/plan9/plan9/sys/src/cmd/pr.c

Purpose: Implements Plan 9 `pr`, a file pagination and multi-column formatter with headings, tabs, numbering, margins, and multi-file modes.

Key behavior:
- Parses classic `pr` options: columns, starting page, double-space, tab settings, formfeed, header, input tabs, length, across/multiple files, offset, separator, no heading, width, numbering, balancing, and odd-page padding.
- `pr` opens files/stdin, calculates dates/headings, and loops pages.
- `putpage` emits one page across columns/files with optional line numbers and spacing.
- `nexbuf` fills a page buffer for multi-column output.
- `balance` balances the last page’s columns.
- `get` normalizes input, tab expansion, backspace/escape effects, and EOF across multi-file mode.
- `put` and `putspace` emit output with clipping and output tab compression.
- Open errors are deferred/printed cleanly.

Dependencies and integration:
- Uses Plan 9 `Bio`, `Dir`, `dirstat`, runes, and standard libc.

Risks and notes:
- Fixed `NFILES` limit of 20.
- Many formatting globals interact; option order matters in places.
- Multi-column buffering can fail with page-buffer overflow if sizing assumptions are wrong.
