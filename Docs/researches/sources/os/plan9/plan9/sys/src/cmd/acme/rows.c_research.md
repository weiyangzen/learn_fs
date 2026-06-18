# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/rows.c

This file manages Acme’s top-level row, columns, workspace dump/load, and all-window traversal.

Key behavior:
- `rowinit()` creates the row tag with commands `Newcol Kill Putall Dump Exit`.
- `rowadd()`, `rowclose()`, `rowresize()`, and `rowdragcol()` manage column layout.
- `rowwhich()` and `rowtype()` route mouse/keyboard events to row, column, tag, or body text.
- `rowdump()` serializes current working directory, fonts, column positions, windows, tags, dirty file contents, zerox relationships, and external command windows.
- `rowloadfonts()` preloads font choices from a dump file.
- `rowload()` reconstructs layout from a dump file, reopens files, restores dirty dumped contents, fonts, and selections.
- `allwindows()` applies a callback to every window.

Important details:
- Dump format uses line records starting with `f`, `F`, `x`, and `e`.
- Dirty buffers can be embedded in the dump; clean files are reopened by name.
- External event windows can be skipped or restored through command metadata.
- Column positions are stored as percentages.

Filesystem relevance:
- High: implements Acme session persistence via dump files and reloads real or embedded file contents.
