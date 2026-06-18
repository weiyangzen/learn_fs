# sources/user-network-fs/samba/source3/modules/vfs_shadow_copy.c

## Purpose
`vfs_shadow_copy.c` is the older shadow-copy module that exposes snapshot directories named exactly like `@GMT-YYYY.MM.DD-HH.MM.SS` at the share root while hiding those directories from normal listings.

## Important APIs, Types, And Functions
- `shadow_copy_match_name()` recognizes fixed-length `@GMT-` labels.
- `shadow_copy_fdopendir()` reads the real directory, filters out `@GMT` entries, copies remaining `struct dirent` values into a private `shadow_copy_Dir`, closes the real DIR/fd, and returns the private object as `DIR *`.
- `shadow_copy_readdir`, `shadow_copy_rewinddir`, and `shadow_copy_closedir` operate on the private directory buffer.
- `shadow_copy_get_shadow_copy_data()` opens the share root and enumerates `@GMT` labels for Windows shadow-copy queries.

## Control Flow
Directory open delegates to the next VFS layer, consumes all entries immediately, hides snapshot labels, and substitutes an in-memory directory iterator. Shadow-copy data enumeration independently opens `conn->connectpath` through Samba directory APIs and counts or copies labels depending on the `labels` flag.

## State And Persistence
The module stores transient directory-list buffers only. Snapshot persistence is external: directories must already exist at the share root with correct `@GMT` names.

## Dependencies And Integration Points
It depends on Samba directory APIs (`OpenDir`, `ReadDirName`), VFS directory hooks, `ntioctl` shadow-copy data types, and a debug class named `shadow_copy`. It registers as `shadow_copy`.

## Risks
- Snapshot labels must exactly match the sample length and prefix; no timestamp validation beyond string shape.
- `shadow_copy_fdopendir()` closes the real DIR and fd after snapshotting entries, so directory changes after open are not reflected.
- Copying raw `struct dirent` into a realloc array assumes the platform struct contains enough fixed storage for names as used by Samba.
- The module only discovers snapshots at the share root.

## Test Signals
- Create root-level `@GMT-YYYY.MM.DD-HH.MM.SS` directories and verify shadow-copy enumeration returns them.
- Normal directory listings should hide those `@GMT` directories.
- Rewind and close on the synthetic DIR should behave correctly.
- Malformed `@GMT`-prefixed names should be ignored.
