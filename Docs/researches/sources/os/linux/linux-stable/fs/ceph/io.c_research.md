# File Research: sources/os/linux/linux-stable/fs/ceph/io.c

## Role

`io.c` provides CephFS I/O mode serialization helpers. It coordinates buffered reads/writes with direct I/O by using `inode->i_rwsem` and the Ceph inode flag `CEPH_I_ODIRECT`.

The design is borrowed from NFS and lets same-mode operations run concurrently while forcing transitions between buffered and direct I/O to drain or flush the incompatible mode.

## Main Entry Points

- `ceph_start_io_read()`
- `ceph_end_io_read()`
- `ceph_start_io_write()`
- `ceph_end_io_write()`
- `ceph_start_io_direct()`
- `ceph_end_io_direct()`

All start functions are declared `__must_check` in `io.h`.

## Buffered I/O Path

`ceph_start_io_read()` takes `inode->i_rwsem` for read optimistically. If `CEPH_I_ODIRECT` is already clear, buffered reads can proceed in parallel. If direct I/O mode is active, it drops the read lock, takes the write lock, calls `ceph_block_o_direct()`, then downgrades to a read lock.

`ceph_start_io_write()` takes `inode->i_rwsem` for write and calls `ceph_block_o_direct()`.

`ceph_block_o_direct()` requires the write side of `i_rwsem`. It clears `CEPH_I_ODIRECT_BIT` under `ci->i_ceph_lock` with memory barriers and, if direct I/O was active, calls `inode_dio_wait()` after dropping the spinlock. This drains outstanding direct I/O before buffered operations proceed.

End functions release the corresponding lock: buffered reads call `up_read()`, buffered writes call `up_write()`.

## Direct I/O Path

`ceph_start_io_direct()` takes `i_rwsem` for read optimistically. If `CEPH_I_ODIRECT` is already set, concurrent direct I/O can proceed. Otherwise it upgrades through a write-lock slow path, calls `ceph_block_buffered()`, and downgrades to read lock.

`ceph_block_buffered()` requires the write side of `i_rwsem`. It sets `CEPH_I_ODIRECT_BIT` under `i_ceph_lock` with memory barriers and, when switching from buffered mode, calls `filemap_write_and_wait()` to flush buffered dirty pages before direct I/O proceeds.

`ceph_end_io_direct()` releases the shared read lock.

## Concurrency Model

- `inode->i_rwsem` is the coarse mode-transition lock.
- `ci->i_ceph_lock` protects the `CEPH_I_ODIRECT` flag.
- Memory barriers around atomic bit changes ensure flag state is visible consistently.
- Same-mode reads/direct I/O can share the read lock.
- Buffered writes and truncates use the write lock and serialize with all direct I/O and buffered reads.

## Important Behavior

- Direct I/O mode blocks buffered I/O until direct I/O is drained.
- Buffered mode blocks direct I/O until buffered writes are flushed.
- Killable lock acquisition propagates interruption errors from `down_read_killable()` or `down_write_killable()`.
- A FIXME notes possible future use of `unmap_mapping_range()` when blocking buffered I/O.
