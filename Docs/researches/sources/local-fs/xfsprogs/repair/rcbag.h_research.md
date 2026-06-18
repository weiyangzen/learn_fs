# File Research: sources/local-fs/xfsprogs/repair/rcbag.h

## Role

`rcbag.h` declares the refcount bag abstraction used by rmap/refcount reconstruction.

## Interface

It exposes bag lifecycle, add/count operations, edge calculation, removal by ending block, distinct-inode iteration, and debug dumping. `struct rcbag_iter` carries a btree cursor and current inode owner.

## Dependencies

The API references XFS mount, rmap record, and btree cursor types.

## Risk Areas

Callers must bracket inode iteration with `rcbag_ino_iter_start()` and `rcbag_ino_iter_stop()` and must not treat `rcbag_count()` as a distinct-record count.
