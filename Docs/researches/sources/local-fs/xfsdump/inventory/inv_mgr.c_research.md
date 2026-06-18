# File Research: sources/local-fs/xfsdump/inventory/inv_mgr.c

Coordinates inventory database initialization, token creation, cross-filesystem searches, inventory printing/checking, reconstruction insertion, and directory creation.

Key functions:
- `init_idb()` ensures inventory directory availability, resolves the filesystem inventory filename, opens or creates `.InvIndex`, and returns either an fd or sentinel.
- `get_token()`, `destroy_token()`, and `get_sesstoken()` allocate internal token descriptors.
- `search_invt()` scans index entries and storage-object session headers in reverse chronological order, skipping pruned sessions and optionally filtering by filesystem UUID.
- `invmgr_query_all_sessions()` searches every filesystem in fstab and handles ambiguous multiple hits.
- `invmgr_inv_print()` and `invmgr_inv_check()` implement inventory display and time-range consistency checks.
- Search callbacks implement “last lower dump level”, “last equal level”, and time-only lookups.
- `insert_session()` reconstructs inventory state from packed session info.
- `make_invdirectory()` recursively creates the inventory directory path.

Important dependencies:
- Connects fstab, index, and storage-object layers.
- Uses callbacks from `inv_stobj.c` for exported session construction and UUID/label matching.

Notable observations:
- `insert_session()` has inverted-looking error logic: it sets `ret = BOOL_TRUE` when insert/time update fails, then returns `BOOL_FALSE` if `ret` is true.
- `inv_priv.h` declares `init_idb()` as returning `bool_t`, while implementation returns `int` sentinels/fds.
- Global lock-file helpers are inside `#ifdef NOTDEF`; normal locking is per-file with `flock()`.
