# File Research: sources/local-fs/squashfs-tools/squashfs-tools/tar.h

This header defines tar header structures, GNU sparse header structures, tar-entry state, tar type constants, and the public tar processing interface.

Key structures:
- `struct tar_header`: 512-byte tar header overlay with raw signed/unsigned views and named fields.
- `struct sparse_entry`, `short_sparse_header`, `long_sparse_header`: GNU sparse metadata formats.
- `struct file_map`: sparse extent pair.
- `struct tar_file`: parsed tar entry with stat data, xattrs, sparse map, path/link/user/group strings, and PAX override flags.

Key constants:
- Tar type flags: regular, hardlink, symlink, char, block, directory, FIFO, global/per-file PAX.
- GNU extension types: long name, long link, sparse.
- Magic strings for V7/GNU/ustar.
- Status codes: `TAR_OK`, `TAR_EOF`, `TAR_ERROR`, `TAR_IGNORED`.
- Xattr encodings: base64 and binary.

Public interface:
- `read_tar_file()`: producer that reads tar input and queues metadata/data buffers.
- `process_tar_file(int progress)`: consumer/tree builder returning the root squashfs inode.
- Extern option globals for default uid/gid/mode and numeric owner handling.
- Xattr hooks compile to real functions under `XATTR_SUPPORT`, otherwise no-op macros.

Important detail:
- `S_IFHRD` is encoded as `S_IFMT`, creating a synthetic mode class for tar hardlink entries before they are resolved to real inode references.
