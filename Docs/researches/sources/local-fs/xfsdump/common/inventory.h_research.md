# File Research: sources/local-fs/xfsdump/common/inventory.h

## Role

This header declares xfsdump's abstract inventory subsystem API and public inventory data structures.

The inventory records every dump session unless explicitly removed and exposes filesystem/session/media queries without exposing the private on-disk database layout.

## Public Types

- `inv_predicate_t`: lookup selector for UUID, mount point, or device path.
- `inv_stream_t`: public stream summary, including interruption state, start/end inode positions, and media-file count.
- `inv_session_t`: public dump-session summary with filesystem UUID, session UUID, stream array, time, level, label, mount point, and device path.
- `inv_mediafile_t`: public media-file descriptor with media object UUID, inode range, and label.
- `inv_inolist_t`: linked list of inventory-related inode numbers.
- Opaque token types:
  - `inv_idbtoken_t`
  - `inv_sestoken_t`
  - `inv_stmtoken_t`

## API Surface

The header declares lifecycle functions:

- `inv_open()` / `inv_close()`
- `inv_writesession_open()` / `inv_writesession_close()`
- `inv_stream_open()` / `inv_stream_close()`
- `inv_put_mediafile()`

It also declares query and reconstruction functions:

- `inv_lasttime_level_lessthan()`
- `inv_lastsession_level_lessthan()`
- `inv_lastsession_level_equalto()`
- `inv_get_inolist()`
- `inv_get_session()`
- `inv_put_session()`

## Path Helpers

The inventory path macros resolve through functions:

- `INV_DIRPATH` -> `inv_dirpath()`
- `INV_FSTAB` -> `inv_fstab()`
- `inv_lockfile()`

This lets the implementation decide the active inventory directory and compatibility paths.

## Constraints

`INV_STRLEN` is fixed at 128 bytes for labels, mount points, and device paths. Public structs expose fixed buffers matching that size.
