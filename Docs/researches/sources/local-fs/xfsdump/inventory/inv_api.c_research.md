# File Research: sources/local-fs/xfsdump/inventory/inv_api.c

Implements the public inventory API used by xfsdump/xfsrestore to open inventory databases, create write sessions, create streams, record media files, query prior sessions, reconstruct inventory from packed session records, delete media objects, and print/debug inventory contents.

Key flows:
- `inv_open()` initializes the inventory for a filesystem predicate, creates or opens the filesystem `.InvIndex`, selects the last `.StObj`, and creates a new storage object when the selected one is full.
- `inv_writesession_open()` ensures fstab contains the filesystem, creates an on-disk session header/session record, and updates index start time for newly created index entries.
- `inv_stream_open()`, `inv_put_mediafile()`, and `inv_stream_close()` manage stream records and append linked mediafile records, keeping stream end inode information synchronized.
- `inv_get_sessioninfo()` packs a still-open session into a portable buffer for writing to media; `inv_put_sessioninfo()` reconstructs by inserting unpacked session data.
- Query helpers delegate to `search_invt()` with callbacks for last lower/equal dump level and exact session uuid/label lookup.
- `inv_getopt()` and `inv_DEBUG_print()` implement `-I` inventory printing/checking suboptions.

Important dependencies:
- Uses `inv_priv.h` on-disk structures, token internals, `GET_*`/`PUT_*` macros, and `INVLOCK`.
- Uses `inv_mgr.c` for initialization, search, printing, and reconstruction insertion.
- Uses `inv_idx.c`, `inv_fstab.c`, and `inv_stobj.c` for index, fstab, and storage-object operations.

Notable observations:
- The API assumes callers obey token lifetime order: stream close, write-session close, inventory close.
- String copies into fixed `INV_STRLEN` fields use `strcpy()` and trust upstream lengths.
- `inv_delete_mediaobj()` is wired to `stobj_delete_mobj()`, but the storage-object deletion implementation is effectively incomplete.
- `inv_DEBUG_print()` returns `BOOL_FALSE` after printing, which is intentionally used by `testmain.c` to stop normal debug-test execution.
