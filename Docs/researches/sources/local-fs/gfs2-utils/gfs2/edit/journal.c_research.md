# File Research: sources/local-fs/gfs2-utils/gfs2/edit/journal.c

## Purpose
Implements journal location, dumping, and block-tracing support for `gfs2_edit`.

## Main Elements
- `find_journal_block()`: resolves `journalN` through `jindex` and returns journal dinode block and size.
- Journal read helpers:
  - `fsck_readi()` reads inode data and reports the absolute block backing the read.
  - `find_wrap_pt()` locates sequence wrap.
- Descriptor processing:
  - `ld_is_pertinent()` filters descriptors for traced blocks.
  - `print_ld_blks()` prints descriptor target blocks and bitmap state.
  - `process_ld()` decodes descriptor type, length, data count, and target list.
- Trace helpers: `meta_has_ref()` checks whether metadata references a traced block; `get_ldref()` maps descriptor offsets back to referenced blocks.
- `display_log_header()` prints sequence, tail, flags, statfs counters, and timestamp.
- `dump_journal()` iterates the journal, optionally tracing one block through descriptors, metadata, revoke/bitmap context, and detailed block display.

## Dependencies And Integration
Uses current editor globals, libgfs2 journal/inode helpers, metadata display from `hexedit.c`, and GFS2 block printers. Invoked from CLI handling for `journalN`.

## Risk Notes
Primarily read-only, but it follows journal and metadata pointers and exits on some read/type errors. Trace mode mutates global `dmode` and `block` while restoring only the current block around nested display calls.
