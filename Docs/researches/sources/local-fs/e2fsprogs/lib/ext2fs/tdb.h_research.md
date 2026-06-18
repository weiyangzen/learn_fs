# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdb.h

Public header for the bundled TDB library. It defines flags for `tdb_store` and `tdb_open`, error codes, debug levels, `TDB_DATA`, logging/hash callback types, and `struct tdb_logging_context`.

For libext2fs integration, it macro-renames the generic TDB symbols to `ext2fs_tdb_*` names, avoiding collisions with system or Samba TDB libraries. Exposed APIs cover opening, closing, fetching, parsing, storing, appending, deleting, traversal, key iteration, whole-database and chain locking, transactions, sequence numbers, flags/sizes, flush, and debug/freelist utilities.

The context is opaque as `struct tdb_context` / `TDB_CONTEXT`; implementation details live in `tdb.c`.
