# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar.c

This file implements `sqfstar` tar ingestion: it reads tar headers and file data from stdin, handles tar/PAX/GNU extensions, queues file data for compression, and builds the Squashfs directory tree from tar entries.

Key phases:
- Header parsing in `read_tar_header`.
- Data buffering in `read_tar_data`.
- Reader loop in `read_tar_file`.
- Tree construction and final directory scan in `process_tar_file`.

Tar format handling:
- Supports V7/ustar/GNU-style header fields, octal and base-256 numeric encodings, signed mtimes, long names/links, global and per-file PAX headers.
- Recognizes regular files, directories, symlinks, hardlinks, char/block devices, FIFOs, GNU sparse files, and PAX sparse variants.
- Handles `LIBARCHIVE.xattr.*` and `SCHILY.xattr.*` through `read_tar_xattr` when xattr support is enabled.
- Skips leading `/`, `./`, and `../` path components and rejects path components `.` or `..` during tree insertion.

Sparse file handling:
- GNU old sparse headers are parsed by `read_sparse_headers`.
- PAX sparse 1.0 maps are parsed by `read_sparse_map`.
- `check_sparse_map` validates that data extents plus holes match the logical file size.
- `read_sparse_block` synthesizes zero-filled holes while reading real data from stdin.

Tree behavior:
- `add_tarfile` creates/intersects directory entries, rejects conflicting file/directory definitions, and optionally copies hardlink targets when `no_hardlinks` is set.
- `lookup_pathname` resolves hardlink targets already seen in the tar stream.
- `fixup_tree` creates default inode metadata for implicit directories and empty subdirectory structures for explicit empty directories.

Important globals/options:
- `ignore_zeros`, `default_uid/gid/mode`, `numeric_owner`, fragment flags, root/global override options, queues, and progress state.
- `sequence` orders metadata/data buffers through queues.

Corruption-sensitive details:
- Header checksum accepts both unsigned and historical signed byte sums.
- Unknown tar types are ignored after skipping their data.
- Truncated reads call `BAD_ERROR` or return `TAR_ERROR`.
- Negative timestamps are rounded to epoch in `new_inode` because Squashfs cannot store pre-1970 times.
