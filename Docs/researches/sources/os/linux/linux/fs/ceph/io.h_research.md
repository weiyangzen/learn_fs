# File Research: sources/os/linux/linux/fs/ceph/io.h

## Purpose

`io.h` declares the CephFS buffered/direct I/O coordination helpers implemented in `io.c`.

## Public API

- `int __must_check ceph_start_io_read(struct inode *inode);`
- `void ceph_end_io_read(struct inode *inode);`
- `int __must_check ceph_start_io_write(struct inode *inode);`
- `void ceph_end_io_write(struct inode *inode);`
- `int __must_check ceph_start_io_direct(struct inode *inode);`
- `void ceph_end_io_direct(struct inode *inode);`

The `__must_check` annotation on start helpers is important: a failed start means no rwsem was acquired and the matching end helper must not be called.

## Dependencies

The header includes `linux/compiler_attributes.h` for `__must_check` and relies on users having visibility of `struct inode`.

## Integration Notes

This header is the narrow contract for CephFS I/O mode serialization. Buffered read/write and direct I/O implementation files should include it and pair each successful start with the matching end operation.
