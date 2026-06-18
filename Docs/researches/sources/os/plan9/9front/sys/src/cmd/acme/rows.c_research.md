# File Research: sources/os/plan9/9front/sys/src/cmd/acme/rows.c

This file manages the top-level Acme row, columns, session dump/load, and all-window traversal.

Key responsibilities:
- `rowinit()` initializes the row tag with `Newcol Kill Putall Dump Exit`.
- `rowadd()` inserts or creates a column, splitting horizontal space.
- `rowresize()` resizes the row and proportionally resizes columns.
- `rowdragcol()` handles column drag/reorder/resize.
- `rowclose()` removes a column and expands neighbors.
- `rowwhichcol()`/`rowwhich()` map screen points to columns/texts.
- `rowtype()` routes keyboard input to the relevant text/window under locking.
- `rowclean()` checks all columns.
- `rowdump()` writes Acme session state to a dump file:
  - working directory
  - font names
  - column percentages
  - window records
  - control state
  - tags
  - dumped body content for dirty/unnamed files
  - external command reconstruction data
- `rowloadfonts()` preloads font names from a dump file.
- `rowload()` restores columns, windows, fonts, file windows, dumped contents, Zerox relationships, external windows, selections, scroll positions, and tags from a dump file.
- `allwindows()` visits every window in every column.

Important dependencies:
- Uses `Biobuf`, file create/open, temp files, window/text/file APIs, command `run()`, and logging.

Filesystem/storage relevance:
- Implements Acme session persistence via `$home/acme.dump` by default.
- Restores real files from disk or dumped buffer contents depending on dirty/availability state.
- Uses temp files when restoring dumped window bodies.

Notes:
- Multiline tag newlines are encoded as byte `0xff` in dump files and decoded on load.
- Windows with open event files are treated specially to avoid dumping externally controlled state unless `dumpstr` is present.
