# File Research: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.c

## Purpose
Main implementation and entry point for `gfs2_edit`: an interactive curses hex/structure/extended editor plus command-line metadata inspection, mutation, savemeta/restoremeta, journal dump, and resource-group repair tool.

## Main Elements
- UI framework: title rendering, help screen, color setup, `bobgets()` input editor, curses interaction loop, and mode switching among hex, structure, and extended views.
- Block display:
  - `display_block_type()` identifies metadata type and resource group allocation state.
  - `hexdump()` renders block bytes, ASCII, field labels, pointer hints, and trace references.
  - `display()` reads the active block, decodes superblock/dinode/indirect/leaf context, and calls raw/structured/extended display.
- Navigation: block history stack, goto keywords, pointer jumps, paging, home/back/forward behavior.
- Keyword and lookup helpers: master-directory lookup, rindex/RG lookup, journal keyword handling, metadata-type search, block type/RG/bitmap/allocation reporting.
- Mutators:
  - `hex_edit()` writes modified bytes to the device.
  - `process_field()` reads or assigns named metadata fields.
  - `find_change_block_alloc()` changes bitmap allocation state.
  - `set_rgrp_flags()` changes resource group flags.
  - `rg_repair()` reconstructs damaged rgrp/bitmap metadata conservatively.
- CLI parsing: two-pass parameter handling supports `-p`, `-x`, `-d`, `-s`, `identify`, `savemeta`, `savemetaslow`, `savergs`, `restoremeta`, `printsavedmeta`, journal dumps, and RG commands.
- `main()`: allocates global state, opens device read-write, reads superblock/rindex/master directory, processes commands, runs interactive or print mode, and frees state.

## Dependencies And Integration
Central coordinator for `gfs2_edit`. Integrates libgfs2 buffer/inode/rgrp APIs, curses, `gfs2hex.c`, `extended.c`, `journal.c`, `savemeta.c`, and `struct_print.c`.

## Risk Notes
This tool opens devices read-write by default and includes direct metadata mutation paths. Several command-line operations call `exit()` deep in helpers. Editing, bitmap changes, RG repair, and restore paths require extreme care on live or valuable filesystems.
