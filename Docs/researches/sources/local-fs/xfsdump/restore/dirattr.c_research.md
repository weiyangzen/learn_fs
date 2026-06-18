# File Research: sources/local-fs/xfsdump/restore/dirattr.c

## Role

`dirattr.c` implements a persistent scratch registry for directory attributes during `xfsrestore`. Directory metadata is read during the directory dump phase, but it cannot be applied immediately because later file restoration and directory creation would disturb timestamps, inherit flags, and related metadata. This module records directory attributes and directory extended attributes, then exposes them later by opaque `dah_t` handles.

## Backing Files

The module creates files in the restore housekeeping directory:

- `dirattr`: primary backing store for fixed-size `struct dirattr` records.
- `dirextattr`: secondary backing store for variable-size directory extended attribute records.

`create_filled_file()` creates a file, attempts to reserve space with `fallocate()` if available, then falls back to `XFS_IOC_RESVSP64`. Reservation failures other than unsupported ioctl/device are logged but do not prevent use.

## Persistent and Transient State

- `struct dirattr_pers` contains `dp_appendoff`, the next append offset in the `dirattr` file.
- `struct dirattr_tran` holds pathnames, file descriptors, append/cache state, a 32 KiB buffered write area, and extattr-file status.
- `DIRATTR_PERS_SZ` is one page (`pgsz`), and the persistent header is mmapped through `mmap_autogrow()`.
- `dah_t` handles encode an index into the backing store. With `DIRATTRCHK`, upper bits also contain a checksum and records contain a unique marker.

## Record Format

`struct dirattr` stores:

- Mode, uid, gid.
- atime, mtime, ctime.
- XFS xflags, extsize, project ID.
- DM event mask and state.
- Offset to the first directory xattr record in `dirextattr`, or `DIRATTR_EXTATTROFFNULL`.

Offsets convert through:

- `DIX2OFF(dix)`: directory attribute index to file offset.
- `OFF2DIX(doff)`: file offset to directory attribute index.

## Initialization and Cleanup

`dirattr_init(hkdir, resume, dircnt)`:

- Allocates transient state once.
- Opens an existing `dirattr` file on resume or creates a new pre-sized one based on `dircnt`.
- mmaps the persistent header.
- Initializes `dp_appendoff` for fresh sessions.
- Builds `dirextattr` pathname and removes any stale extattr file on resume.

`dirattr_cleanup()`:

- Unmaps the persistent header.
- Closes both backing files.
- Unlinks `dirattr` and `dirextattr`.
- Frees pathnames and transient state.

## Adding and Updating Directory Attributes

`dirattr_add(filehdr_t *fhdrp)`:

- Ensures the main file descriptor is positioned at `dp_appendoff`.
- Flushes the 32 KiB buffer if needed.
- Converts the file header's `bstat_t` fields into a `dirattr_t`.
- Initializes xattr offset to null.
- Buffers the record, advances `dp_appendoff`, and returns a handle.

`dirattr_update(dah, fhdrp)`:

- Validates and locates the existing record.
- Flushes pending append-buffer data if necessary.
- Seeks directly to the record and overwrites it with metadata from the new file header.
- Resets the record's extattr offset to null.

`dirattr_del()` is currently a no-op.

## Reading and Caching

`dirattr_get(dah)` is the internal cache loader:

- Returns immediately when the requested handle is already cached.
- Validates handle/index bounds.
- Flushes pending appended records before random reading.
- Seeks and reads the record into `dt_cached_dirattr`.
- Under `DIRATTRCHK`, validates unique marker and checksum.

Getter functions (`dirattr_get_mode()`, `dirattr_get_uid()`, etc.) all call `dirattr_get()` and return a field from the cached record.

`dirattr_cacheflush()` writes the cached record back to its backing-store location. It is used when adding the first extended attribute to a directory updates the cached `d_extattroff`.

`dirattr_flush()` writes pending buffered fixed-size directory records to the `dirattr` file and resets the buffer offset.

## Directory Extended Attributes

`dirattr_addextattr(dah, ahdrp)` stores a directory xattr in `dirextattr`:

- Loads the owning directory record into cache.
- Lazily opens/creates `dirextattr`.
- Walks the offset-linked extattr list to find its tail.
- Appends a new record consisting of:
  - Next-offset field initialized to `DIRATTR_EXTATTROFFNULL`.
  - The full `extattrhdr_t` record and appended name/value payload.
- If this is the first xattr for the directory, updates cached `d_extattroff` and flushes the cached dirattr record.
- Otherwise, writes the new offset into the previous extattr record's next-offset field.

`dirattr_cb_extattr(dah, cbfunc, ahdrp, ctxp)` replays xattrs:

- Loads the directory record.
- Opens/creates `dirextattr` lazily.
- Walks the offset-linked list.
- Reads each next offset, extattr header, and payload into the caller-provided buffer.
- Invokes the callback and stops early if the callback returns false.

The extattr file is treated as optional/degraded: open/read/write/seek failures log warnings, mark `dt_extattrfdbadpr`, and generally return without aborting the restore.

## Error Handling and Invariants

- Uses assertions for handle validity, file offset bounds, record sizes, mmap alignment, and expected seek/read/write sizes.
- I/O failures in primary dirattr operations generally log errors and return `DAH_NULL`, `RV_UNKNOWN`, or assert.
- Extattr side-file failures are downgraded to warnings, so directory restore can continue without directory xattrs.
- `resume` mode requires the primary `dirattr` file to exist but deliberately unlinks the extattr side file.

## Relationship to `content.c`

`content.c` calls:

- `dirattr_init()` when directory dump restore starts or resumes.
- `dirattr_add()` indirectly through tree directory creation to get `dah_t`.
- `dirattr_addextattr()` while reading directory xattr pseudo-files.
- `dirattr_cb_extattr()` after tree post-processing to apply saved directory xattrs.
- `dirattr_flush()` after reading all directory entries.
