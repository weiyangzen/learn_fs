# File Research: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.h

## Purpose
Public declarations for GFS2-specific display and decode helpers.

## Main Elements
- Declares `display_gfs2()`, `edit_gfs2()`, `do_dinode_extended()`, `do_leaf_extended()`, `print_gfs2()`, and `eol()`.
- Exposes global `block`.

## Dependencies And Integration
Includes `hexedit.h` for shared editor types and globals.

## Risk Notes
Declares `edit_gfs2()` although no implementation appears in this group, suggesting historical or external dead declaration.
