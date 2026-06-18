# File Research: sources/local-fs/erofs-utils/lib/tar.c

## Scope

This file implements tar-like stream input for EROFS image generation: buffered stream/decompression wrappers, tar numeric and PAX parsing, tar/PAX xattr collection, hardlink and overlay handling, file data staging, and one-record-at-a-time tree import.

## Public And Internal APIs Covered

- Stream lifecycle and reads: `erofs_iostream_open()`, `erofs_iostream_close()`, `erofs_iostream_read()`, `erofs_iostream_bread()`, and `erofs_iostream_lskip()`.
- PAX/xattr helpers: `tarerofs_insert_xattr()`, `tarerofs_merge_xattrs()`, `tarerofs_remove_xattrs()`, `tarerofs_apply_xattrs()`, and `tarerofs_parse_pax_header()`.
- Tar tree import: `tarerofs_parse_tar()`.
- Inode removal/staging helpers: `tarerofs_remove_inode()`, `tarerofs_write_uncompressed_file()`, and `tarerofs_write_file_data()`.
- Internal parsers include octal/base-256 numeric parsing and percent-decoding for libarchive xattr names.

## Control Flow And Behavior

- `erofs_iostream_open()` configures the stream for plain fd, gzip, liblzma, gzip-random-access builder, or tar dump mode; plain files are size-detected with `lseek()` and advised sequentially when available.
- `erofs_iostream_read()` maintains a head/tail buffer, compacts unread bytes, fills from the selected decoder, optionally dumps raw bytes, marks EOF, and returns an in-buffer slice rather than always copying.
- `erofs_iostream_lskip()` skips buffered bytes first, uses `lseek()` for seekable plain streams when no dump is active, and otherwise drains through the decoder.
- `tarerofs_parse_pax_header()` consumes PAX records of the form `LEN NAME=VALUE\n`, updating path, linkpath, size, uid/gid, mtime/nsec, and xattrs. It supports SCHILY xattrs as raw values and LIBARCHIVE xattrs as URL-decoded names with base64-decoded values.
- `tarerofs_parse_tar()` aligns to 512-byte records, reads a tar header, validates checksum with unsigned and signed checksum variants, handles two zero blocks as end-of-archive, rejects invalid magic, and interprets POSIX/GNU type flags.
- GNU volume headers set the EROFS volume name. Global and per-file PAX headers update persistent or current extended header state. GNU long path and long link records populate current path/link overrides.
- Normal tar entries are resolved through `erofs_rebuild_get_dentry()`, including AUFS/overlayfs whiteout and opaque-directory handling. Existing non-directory entries are removed/replaced; existing directories can be reused.
- Hardlinks reuse the target inode, increment link count, and replace an existing destination inode if necessary. Directory hardlinks are rejected.
- Symlink content is copied from the link path. Device nodes encode major/minor into EROFS device format. Regular-file payloads can be zero-filled, stored as tar index chunks, reserved-space references, blob chunks, written uncompressed directly in no-reorder mode, or staged into a disk buffer for later compression/import.
- Local PAX xattrs are merged with global xattrs, then applied with `erofs_vfs_setxattr()`.

## State And Data Structures

- `struct erofs_iostream` tracks decoder type, handler, buffer, head/tail cursors, logical stream size, EOF state, dump fd, and optional gzip-random-access builder.
- `struct erofs_pax_header` carries current/global tar overrides and xattr list.
- `struct tarerofs_xattr_item` stores `name\0value` buffers with explicit name and total lengths.
- `struct erofs_tarfile` controls modes such as AUFS compatibility, index/header-only operation, reserved-space import, no-reorder direct writing, dump file, and source-device id.

## Dependencies

- Optional zlib, liblzma, and gzran support.
- EROFS importer, inode, rebuild, xattr, disk-buffer, blob-chunk, base64, and cache helpers.
- POSIX file APIs for `read`, `lseek`, `pwrite`, `open`, and descriptor lifecycle.

## Risks And Invariants

- Tar offset accounting must stay 512-byte aligned even when payload data is skipped, indexed, or staged.
- PAX parsing treats malformed lengths, missing separators, missing trailing newlines, invalid numeric overrides, and bad base64 as hard errors.
- Stream read sizes are bounded by the current buffer and `INT_MAX`; callers must handle short reads.
- `tarerofs_insert_xattr()` deduplicates by xattr name and either skips existing entries or replaces values depending on caller intent.
- AUFS/overlay conversion mutates inode type and parent directory metadata; incorrect handling would expose whiteouts as ordinary device nodes.
