# File Research: sources/local-fs/gfs2-utils/gfs2/edit/journal.h

## Purpose
Header for `gfs2_edit` journal inspection helpers.

## Main Elements
- Declares `dump_journal()`.
- Declares `find_journal_block()`.

## Dependencies And Integration
Included by `hexedit.c` for command handling and by journal-aware display code.

## Risk Notes
Minimal header; callers must already have global editor/libgfs2 state initialized.
