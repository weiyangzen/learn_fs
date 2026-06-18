# File Research: sources/local-fs/gfs2-utils/gfs2/edit/extended.h

## Purpose
Header for extended display functions used by `gfs2_edit`.

## Main Elements
- Declares `do_indirect_extended()`.
- Declares `display_extended()`.

## Dependencies And Integration
Depends on `struct iinfo` from `hexedit.h` being visible before use.

## Risk Notes
No standalone includes for dependent types; include ordering matters.
