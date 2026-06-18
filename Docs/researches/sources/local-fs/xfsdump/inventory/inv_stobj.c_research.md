# File Research: sources/local-fs/xfsdump/inventory/inv_stobj.c

Implements storage-object operations. A `.StObj` holds session headers, session records, stream records, and linked mediafile records for one filesystem/time range.

Key functions:
- `stobj_create()` creates and initializes a storage object with `invt_sescounter_t`.
- `stobj_create_session()` and `stobj_put_session()` allocate session header/session/stream space and update counters.
- `stobj_put_mediafile()` appends a mediafile record, updates stream start/end positions, and maintains the linked mediafile chain.
- `stobj_insert_session()` supports reconstruction, rejecting duplicate session IDs and splitting full storage objects.
- `stobj_split()` creates a new storage object, moves later sessions, adjusts index time ranges, and inserts the new session.
- `stobj_pack_sessinfo()` serializes one session, its streams, and mediafiles into the packed inventory format.
- `stobj_unpack_sessinfo()` validates the cookie, handles packed versions 1 and 2, performs endian/architecture translation, and points an `invt_sessinfo_t` into the packed buffer.
- `stobj_make_invsess()`/`stobj_copy_invsess()` convert on-disk structures to public `inv_session_t`.
- `DEBUG_sessionprint()` prints sessions with filtering by depth, dump level, and media object.

Important dependencies:
- Uses `arch_xlate.h` conversion routines for packed session portability.
- Uses index helpers for split/insertion and manager search callbacks for queries.
- Uses `ctime32()` for display.

Notable observations:
- `stobj_delete_mobj()` is mostly stubbed/commented and always returns false to continue iteration; media-object deletion is therefore not functionally complete.
- `stobj_delete_sessinfo()` only decrements the in-memory counter and intentionally leaves data space wasted.
- Packed version 1 alignment workaround leaks a small allocated buffer by design, as documented in comments.
- `stobj_hdrcmp()` subtracts `time32_t` values and returns `int`, which is simple but can overflow if widened ranges are introduced.
