# File Research: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.c

## Purpose
Provides shared global editor state and core GFS2 block decoding for `gfs2_edit`.

## Main Elements
- Defines global display/edit/navigation state: current block, mode, cursor rows, superblock state, indirect data, terminal state, and formatting buffers.
- `eol()` and `print_gfs2()` abstract curses vs stdout output.
- Directory parsing:
  - `idirent_in()` converts on-disk dirents to host fields.
  - `indirect_dirent()` validates and records directory entries.
- `do_dinode_extended()` extracts dinode indirect pointers, stuffed directory entries, or exhash leaf pointers.
- `do_leaf_extended()` parses a leaf block and returns its continuation block.
- `do_eattr_extended()` prints extended attribute entries.
- `display_gfs2()` dispatches typed structure printing by GFS2 metatype.

## Dependencies And Integration
Uses libgfs2 endian/metadata helpers and `struct_print.c` printers. Supplies globals consumed by `hexedit.c`, `extended.c`, `journal.c`, and `savemeta.c`.

## Risk Notes
`print_gfs2()` uses `vsprintf()` into a fixed `PATH_MAX` buffer. Directory parsing uses block-size assumptions and stops on malformed record lengths.
