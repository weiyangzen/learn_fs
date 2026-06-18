# File Research: sources/local-fs/erofs-utils/lib/liberofs_fragments.h

This header declares packed-fragment support for deduplicating and storing file fragments in a packed inode.

API:
- `z_erofs_fragments_tofh()` computes a fragment hash-like value from file data.
- `erofs_fragment_findmatch()` searches for a matching fragment.
- `erofs_pack_file_from_fd()` packs file data from a vfile/fpos.
- `erofs_fragment_pack()` packs an in-memory fragment region.
- `erofs_fragment_commit()` finalizes fragment metadata for an inode.
- `erofs_flush_packed_inode()` flushes packed inode state at importer finalization.
- `erofs_packedfile()` returns or creates packed file support for an sb.

Known users:
- `importer.c` initializes packed files when fragments, compressed dirs, or extra xattr prefix handling require it, and flushes packed inode data before final metadata flush.
- `inode.c` treats packed inode as a special identifier and avoids extended inode layout for it.

Risk / note:
- The API is tightly coupled to compression/fragments and must be flushed before the main buffer manager is flushed.
