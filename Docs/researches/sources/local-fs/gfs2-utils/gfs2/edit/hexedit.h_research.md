# File Research: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.h

## Purpose
Shared declarations, constants, global state, and small inline helpers for the `gfs2_edit` modules.

## Main Elements
- Display modes: `HEX_MODE`, `GFS2_MODE`, `EXTENDED_MODE`, `INIT_MODE`.
- Special pseudo-blocks: `RGLIST_DUMMY_BLOCK`, `JOURNALS_DUMMY_BLOCK`.
- Global externs for editor state, block history, terminal/curses state, current superblock, dinode, indirect info, and options.
- Structures:
  - `idirent`: host-format directory entry view.
  - `indirect_info` and `iinfo`: pointer/dirent/leaf display data.
  - `blkstack_info`: navigation history snapshot.
- Color macros for curses output.
- Public functions for block identity, display, save/restore, keyword parsing, master lookup, and metadata type detection.

## Dependencies And Integration
Included by nearly every `gfs2/edit` C file and anchors shared mutable state across modules.

## Risk Notes
Large global-state surface makes module behavior order-dependent. Some declarations depend on libgfs2 and curses types, so this header is not lightweight.
