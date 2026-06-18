# sources/test-tools/fio/engines/splice.c

## Purpose
`splice.c` implements fio's synchronous Linux splice/vmsplice ioengine. It measures data paths that move bytes through pipes using `splice(2)` and `vmsplice(2)` rather than ordinary `read`/`write`.

## Important APIs, Types, And Functions
`struct spliceio_data` owns a pipe and two feature flags: whether `vmsplice` to user memory is usable and whether the mmap-assisted path works. `fio_splice_read_old()` splices file data into a pipe and reads the pipe into the user buffer. `fio_splice_read()` uses `splice` into a pipe then `vmsplice` into the fio buffer, optionally via a temporary mapping. `fio_splice_write()` vmsplices the fio buffer into a pipe and splices to the file. `fio_spliceio_queue()` dispatches directions and maps return counts to fio completion state.

## Control Flow
`.init` allocates state, creates a pipe, and optimistically enables modern vmsplice paths. `.queue` handles reads, writes, TRIM, and sync directions synchronously. Read first tries the vmsplice-to-user path; if the kernel returns `EBADF`, it disables that capability and retries the old pipe-read path. Write waits for pipe writability, moves buffer pages into the pipe, then drains them to the file at the target offset. `.cleanup` closes pipe fds and frees state.

## State And Persistence
Engine state is limited to pipe descriptors and capability flags. Data persists in the underlying file for writes. The mmap-assisted read path temporarily maps over `io_u->xfer_buf` and unmaps before returning.

## Dependencies And Integration Points
The engine depends on Linux `splice`, `vmsplice`, `pipe`, `poll`, `mmap`, fio generic file helpers, `SPLICE_DEF_SIZE`, and synchronous engine accounting through `FIO_SYNCIO | FIO_PIPEIO`.

## Risks
Return-value sign handling is inconsistent: some helpers return `-errno`, but `fio_spliceio_queue()` sets `io_u->error = errno` rather than `-ret`, so stale `errno` could be reported. The mmap path maps at `io_u->xfer_buf`, which is unusual and can fail or interact badly with buffer ownership. Partial splice/vmsplice behavior needs careful residual handling. Unsupported filesystem/device paths surface as `EINVAL`.

## Test Signals
Tests should cover read fallback from vmsplice to old mode, write path through pipe, short transfers, TRIM/sync delegation, unsupported filesystem error messaging, and cleanup after pipe creation failure. Integration tests need Linux kernels/filesystems with splice support.
