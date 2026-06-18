# sources/sync-backup/rsync/ifuncs.h

## Purpose

`ifuncs.h` defines small inline helpers used throughout rsync. The functions cover dynamic buffers, wire-mode portability, directory-entry name quirks, `stat_x` initialization/freeing, and allocation-backed string duplication.

## Important APIs, Types, And Functions

`alloc_xbuf(xbuf *xb, size_t sz)` allocates an `xbuf` buffer with zero length and position. `realloc_xbuf(xbuf *xb, size_t sz)` resizes an existing buffer through rsync's checked `realloc_array()`. `free_xbuf(xbuf *xb)` frees the buffer and clears the structure.

`to_wire_mode(mode_t mode)` maps platform symlink mode bits to rsync's wire value `0120000` when the local `_S_IFLNK` differs. `from_wire_mode(int mode)` maps that wire value back to local mode bits. `d_name(struct dirent *di)` hides `HAVE_BROKEN_READDIR` by returning `di->d_name - 2` on affected systems. `init_stat_x(stat_x *sx_p)` initializes create-time, ACL, and xattr fields. `free_stat_x(stat_x *sx_p)` frees ACL/xattr side data only when the corresponding preserve options are enabled. `my_strdup()` allocates and copies a string using `my_alloc()` and source location metadata.

## Control Flow

All functions are direct inline helpers. The mode conversion helpers conditionally rewrite only symlink type bits. `free_stat_x()` uses scoped `extern` declarations for `preserve_acls` and `preserve_xattrs` so callers can clean up optional data without duplicating feature checks.

## State, Dependencies, And Integration

The helpers have no persistent state. They depend on `rsync.h` types and allocation wrappers, ACL/xattr cleanup functions when compiled, and feature macros. `flist.c`, `generator.c`, `hlink.c`, and other modules use `init_stat_x()`/`free_stat_x()` around metadata comparisons and transfer setup; file-list serialization uses mode conversion helpers.

## Risks

Because these functions are inline and widely included, changes can affect many modules. `realloc_xbuf()` does not preserve the old pointer on failure because `realloc_array()` is expected to be fatal or checked by rsync allocation policy. `free_stat_x()` only frees optional data when preserve flags are currently enabled, so callers must keep flag state consistent with how the `stat_x` was populated. `d_name()` encodes a platform workaround that would be dangerous if enabled incorrectly.

## Test Signals

Compile with and without symlink support, ACLs, xattrs, and broken-readdir simulation. Test wire-mode round trips on platforms with nonstandard symlink bits, xbuf allocation/reallocation/free, and `stat_x` cleanup after ACL/xattr population.
