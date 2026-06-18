# File Research: sources/local-fs/xfsdump/invutil/stobj.c

Implements interactive handling of inventory storage-object files. Storage objects contain session headers, sessions, streams, and media-file records.

Core behavior:
- Opens storage-object files with exclusive locks and mmap write access.
- Builds hierarchical menu nodes for sessions, streams, and media files.
- Displays detailed info for highlighted sessions/streams/media files.
- Maps delete/undelete/select/commit actions to inventory record mutations.
- Marks session headers pruned by setting `sh_pruned`.
- Unlinks a storage-object file on close if every session is pruned.

Key functions:
- `generate_stobj_menu()` walks mapped storage-object records and creates hidden child menu nodes.
- `open_stobj()` opens, stats, mmaps, duplicates file name, and registers file metadata.
- `close_all_stobj()` closes all opened storage-object files and unlinks fully pruned ones.
- `stobjsess_commit()` commits deletion state back into `invt_seshdr_t.sh_pruned`.
- `stobj_prune()` tests whether an interactive node should be auto-marked for pruning by mountpoint/UUID/date.
- highlight handlers populate the info window with fields from inventory records.

Data model:
- Global `stobj_file` array stores mmap address, size, fd, counter, filename, and per-record pointers.
- `stobjsess_t` pairs session headers with session bodies for menu callbacks.

Risks/assumptions:
- Binary offsets in inventory records are trusted.
- Uses global mutable state and is not thread-safe.
- Some snprintf length calculations are tight but generally include fixed label lengths.
- File unlink is deferred until close and based solely on `sh_pruned` state.
