# File Research: sources/os/linux/linux-stable/fs/ceph/io.h

## Role

`io.h` is the local CephFS header for I/O mode coordination helpers implemented in `io.c`.

## Contents

It has a standard include guard `_FS_CEPH_IO_H`, includes `<linux/compiler_attributes.h>`, and declares:

- `int __must_check ceph_start_io_read(struct inode *inode);`
- `void ceph_end_io_read(struct inode *inode);`
- `int __must_check ceph_start_io_write(struct inode *inode);`
- `void ceph_end_io_write(struct inode *inode);`
- `int __must_check ceph_start_io_direct(struct inode *inode);`
- `void ceph_end_io_direct(struct inode *inode);`

## Contract

Callers must check the start helpers because they may fail on killable lock acquisition. A successful start helper must be paired with the matching end helper to release `inode->i_rwsem`.
