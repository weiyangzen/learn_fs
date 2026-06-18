# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.c

Core `unsquashfs`/`sqfscat` entry point. It owns global extraction state, CLI option parsing, filesystem opening/validation, read/decompression/write threading, path filtering, listing, pseudo-file generation, and final summary/exit status.

Key responsibilities:
- Maintains global runtime knobs: processor count, progress flags, strict/ignore error behavior, xattr filters, destination path, max depth, listing/cat/pseudo modes, forced uid/gid, and filesystem block metadata.
- Implements bounded thread-safe queues and cache structures used by the reader, inflator, writer, progress, and info paths.
- Reads Squashfs metadata via `read_fs_bytes()`, `read_block()`, `read_metadata()`, `read_inode_data()`, and `read_directory_data()`, including start-offset handling and endian/compression handling through `comp`.
- Restores extracted filesystem objects: regular files, symlinks, devices, FIFOs, sockets, hard links, directories, timestamps, modes, ownership, sparse holes, and xattrs.
- Resolves extract/exclude path trees using exact, wildcard, or POSIX regex matching. It canonicalizes relative symlink traversal, prevents excessive symlink depth, tracks directory loops by inode number, and supports sticky excludes prefixed with `"... "`.
- Implements `sqfscat` mode by resolving requested paths to regular files and writing file contents to stdout.
- Implements pseudo output mode in two passes: first emits pseudo metadata and computes byte offsets, then cats regular file payloads after a `START OF DATA` marker.
- Parses options for both `unsquashfs` and `sqfscat`, including memory sizing, queue sizing, xattr policy, help dispatch, pager setup, `SQFS_CMDLINE` logging, offsets, time override, stat/mkfs-time, and extract/exclude file ingestion.
- Main flow: initialize defaults, parse mode-specific options, open filesystem, read superblock from v4/v3/v2/v1 handlers, validate compressor and block sizing, initialize threads, read filesystem tables, resolve filters, optionally pre-scan for progress totals, then scan/extract/list/cat/pseudo.

Concurrency model:
- `reader()` reads compressed blocks requested by `cache_get()`.
- `inflator()` decompresses compressed cache entries.
- `writer()` writes extracted files and directory attributes; `cat_writer()` streams file contents.
- `progress_thread()` periodically renders progress.
- Shared caches use mutexes/condition variables and mark entries pending/error/ready.

Important dependencies:
- Version-specific readers from `unsquash-*.c` through the `squashfs_operations` table.
- `compressor.c` abstraction for decompression and compressor option validation.
- `xattr.h` for `write_xattr()`, `has_xattrs()`, regex filters, and pseudo xattr printing.
- `uid_gid.c`, `limit.c`, `memory.c`, `print_pager.c`, `date.c`, and checksum/sort helpers.

Notable edge handling:
- Avoids signed-int overflows for queue/cache sizing and memory conversions.
- Serializes `lseek()+read()` using `pos_mutex`.
- Handles EINTR for read/write loops.
- Treats fatal/non-fatal extraction failures according to `-ignore-errors`, `-strict-errors`, and `-no-exit-code`.
