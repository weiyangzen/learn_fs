# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_subr.c

## Purpose
Shared HAMMER2 utility routines for type conversion, timestamp conversion, GUID/UUID mapping, directory hashing, block-size calculations, I/O counters, signal checks, and diagnostic strings.

## Type And Time Conversion
`hammer2_get_dtype()`, `hammer2_get_vtype()`, and `hammer2_get_obj_type()` convert between HAMMER2 object types, directory entry types, and vnode types.

`hammer2_time_to_timespec()`, `hammer2_timespec_to_time()`, and `hammer2_update_time()` convert HAMMER2 microsecond timestamps to/from `timespec` and current VFS timestamps.

`hammer2_to_unix_xid()` and `hammer2_guid_to_uuid()` map Unix uid/gid values into/out of a UUID node field.

## Directory Hashing
`hammer2_dirhash()` adapts HAMMER1 directory hashing. It hashes filename segments split by `.`, `-`, `_`, and `~`, sets bit 63, adds a full-name CRC component, and sets bit 15 so readdir cookies can remain positive while preserving low artificial cookie values.

## Block Sizing
`hammer2_getradix()` converts byte sizes to allocation radix, optimized for common HAMMER2 buffer sizes and clamped to minimum allocation where appropriate. `hammer2_calc_logical()` currently always returns `HAMMER2_PBUFSIZE` logical blocks and can return logical base/eof. `hammer2_calc_physical()` returns a smaller physical block size for the file EOF block or zero beyond EOF.

## Counters And Errors
`hammer2_adjreadcounter()` and `hammer2_adjwritecounter()` increment global read/write byte counters by blockref type. `hammer2_signal_check()` periodically yields and detects pending user-thread signals for long operations. `hammer2_error_str()` maps HAMMER2 error bits to human-readable strings. `hammer2_bref_type_str()` maps blockref types to names.

## Integration Notes
These helpers are used throughout HAMMER2 VFS, strategy, directory, inode, and recovery code. The directory hash shape is part of on-disk lookup semantics and must remain stable.
