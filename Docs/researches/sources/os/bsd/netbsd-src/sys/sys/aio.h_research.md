# File Research: sources/os/bsd/netbsd-src/sys/sys/aio.h

Read completely: 233 lines.

Defines POSIX asynchronous I/O public structures and NetBSD kernel-private AIO service state.

Public ABI:
- Defines `AIO_CANCELED`, `AIO_NOTCANCELED`, and `AIO_ALLDONE` return states.
- Defines list I/O opcodes `LIO_NOP`, `LIO_WRITE`, `LIO_READ`.
- Defines list I/O modes `LIO_NOWAIT` and `LIO_WAIT`.
- `struct aiocb` contains file offset, userspace buffer, transfer length, fd, list opcode, request priority, sigevent, and kernel-maintained status fields `_state`, `_errno`, and `_retval`.

Kernel internals:
- Default limits are `AIO_LISTIO_MAX=512` and `AIO_MAX=AIO_LISTIO_MAX*16`.
- Defines operation flags for read/write/sync/dsync and job states none/work-in-progress/done.
- `struct aiowaitgroup` and `struct aiowaitgrouplk` manage suspend/list waiters and references.
- `struct aio_job` tracks one queued operation, its copied aiocb, originating process, file pointer, completion state, waitgroups, and list-I/O request pointer.
- `struct aiost_file_group`, `struct aiost`, and `struct aiosp` implement per-process servicing pools, worker thread lists, pending queues, hash lookup by user aiocb pointer, and per-file grouping.
- `struct aioproc` is per-process AIO state.
- Declares AIO pool, suspend, enqueue, conflict validation, error/return, and waitgroup helper functions.

Risks and notes:
- The public `aiocb` includes kernel status fields, so ABI consumers can observe layout.
- Kernel state is concurrency-heavy: jobs can be on queues, in worker threads, referenced by waitgroups, and found through aiocb pointer hashing.
