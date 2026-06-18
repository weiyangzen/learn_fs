# File Research: sources/local-fs/gfs2-utils/gfs2/edit/savemeta.c

## Purpose
Implements `gfs2_edit` metadata capture, compressed metadata-file format, metadata printing, and dangerous metadata restore.

## Main Elements
- File format:
  - `savemeta_header` with magic, format, timestamp, and filesystem byte size.
  - `saved_metablock` records block number and significant length.
- Compression I/O:
  - `metafd` abstracts raw/gzip/bzip2 reads and gzip writes.
  - Restore buffering uses a 2 MiB window with `restore_buf_next()`.
- Save path:
  - Detects system files, per-node entries, journal dinodes, and significant data length.
  - Saves superblock, rgrps/bitmaps, dinodes, indirect blocks, directory leaves, eattrs, system-file data, and metadata-looking journal contents while avoiding ordinary user data where possible.
  - `savemeta()` writes header, walks the rgtree, saves selected ranges, reports progress, and exits.
- Restore/print path:
  - Detects bzip2/gzip/uncompressed-compatible stream handling.
  - Parses new header or falls back to old format scanning.
  - Restores superblock and saved blocks to a destination device/file, or prints saved block types/details.
  - Truncates restored regular files to saved filesystem size when known.

## Dependencies And Integration
Called from `hexedit.c` CLI modes `savemeta`, `savemetaslow`, `savergs`, `restoremeta`, and `printsavedmeta`. Uses libgfs2 rgrp/inode metadata, editor display routines, zlib, and bzip2.

## Risk Notes
Restore writes raw filesystem blocks and exits on many failures. Save mode deliberately omits most user file data, but system files, directories, symlinks, metadata, and journal metadata are preserved. Format parsing supports old layouts by scanning for the superblock, which is useful but fragile with corrupt input.
