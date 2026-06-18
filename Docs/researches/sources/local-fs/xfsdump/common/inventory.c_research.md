# File Research: sources/local-fs/xfsdump/common/inventory.c

## Role

This file is the public inventory API implementation used by xfsdump/xfsrestore callers to open the inventory database, query previous dump sessions, create new session records, add streams, add media-file records, and close inventory tokens.

It is a facade over the private inventory implementation in `inventory_priv.h` and related inventory modules.

## Major Responsibilities

- Open an inventory database for a filesystem by UUID, mount point, or device path via `inv_open()`.
- Select or create a storage object for session records.
- Close inventory database tokens and the session lock descriptor in `inv_close()`.
- Query the latest previous dump time or session at a level less than or equal to a requested dump level.
- Create a write session with filesystem/session UUIDs, label, level, stream count, timestamp, mount point, and device path.
- Create per-stream records under a session.
- Add per-media-file records to a stream.
- Close streams and sessions while updating end times and interrupted status.

## Key Flows

`inv_open()` initializes the inventory index with `init_idb()`, obtains the current storage object with `get_storageobj()`, checks session-counter capacity, and creates a new storage object/index entry when full. The returned token contains the inventory index descriptor, storage-object descriptor, and index header offset.

`inv_writesession_open()` ensures the fstab-style inventory entry is present, allocates an on-disk session record, fills session identity and label/path fields, creates a session header, serializes the session under an exclusive storage-object lock, and updates inventory start time for a newly created index entry.

`inv_stream_open()` allocates a stream token, locks the session file, reads the session header and session record, reserves the next stream slot if below `s_max_nstreams`, writes the updated session, then writes an empty stream header.

`inv_put_mediafile()` builds an `invt_mediafile_t` and delegates insertion to `put_mediafile()` under an exclusive storage-object lock. The most recent media-file copy remains owned by the stream token until `inv_stream_close()`.

## Query Behavior

The last-time and last-session functions all use `search_invt()` with callback predicates:

- `tm_level_lessthan`
- `lastsess_level_lessthan`
- `lastsess_level_equalto`

They return `BOOL_FALSE` only for search errors. A successful search that finds nothing is represented by a null output pointer.

## Locking And State

- Uses file locks through `INVLOCK()` for storage-object serialization.
- Uses `sess_lock()`/`sess_unlock()` around stream slot allocation.
- Uses a global `sesslock_fd`, closed by `inv_close()` and on some `inv_open()` failure paths.
- Session and stream tokens are heap-allocated private descriptor structures.

## Notable Gaps

`inv_get_inolist()` is effectively disabled under `#ifdef NOTDEF` and currently returns `1` without filling an inode list.

`inv_get_session()` contains assertions and comments but no implementation or return value in this file.

The file uses fixed-size `strcpy()` into inventory label/path fields, relying on callers to respect `INV_STRLEN`.
