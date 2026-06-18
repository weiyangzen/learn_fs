# File Research: sources/os/linux/linux/io_uring/openclose.c

io_uring open, close, fixed-fd install, and pipe operation implementation. This file adapts VFS fd/name operations into io_uring request preparation, async retry, fixed-file table installation/removal, and CQE completion.

Key responsibilities:
- Implements `IORING_OP_OPENAT` and `IORING_OP_OPENAT2`, including `open_how` parsing, delayed pathname capture, `O_LARGEFILE` normalization, `RESOLVE_CACHED` nonblocking retry, normal fd allocation, and fixed-file slot installation.
- Implements `IORING_OP_CLOSE`, including fixed slot removal through `io_fixed_fd_remove()` and normal fd close guarded by `files->file_lock`.
- Implements `IORING_OP_FIXED_FD_INSTALL`, receiving a fixed file into the task fd table with optional `CLOEXEC` suppression.
- Implements pipe creation for normal fd pairs and fixed-file table slots, including allocated-slot mode via `IORING_FILE_INDEX_ALLOC`.
- Provides BPF context population for openat fields.

Important data flows:
- Open prep captures filename with `delayed_getname()`, stores `dfd`, `file_slot`, and `RLIMIT_NOFILE`, and forces async for open modes known to need blocking path work.
- Open issue builds VFS open flags, optionally obtains an fd, calls `do_file_open()`, retries `-EAGAIN` for nonblocking cached lookup, and either installs the fd or calls `io_fixed_fd_install()`.
- Close issue rejects closing io_uring files, punts to async if `->flush` could block, then detaches the fd and calls `filp_close()`.
- Pipe fixed installation creates both pipe files first, installs them under `ctx->uring_lock`, copies fixed indexes to userspace, and rolls back any installed slot on copy failure.

Concurrency and locking:
- Fixed-file table mutation uses `io_ring_submit_lock()`.
- Normal close holds `files->file_lock` while validating and removing the fd.
- Pipe fixed install must serialize both slot installs and rollback under the submit lock.

Notable risks:
- Fixed open rejects `O_CLOEXEC` because fixed-file slots are not process fds.
- Close must avoid io_uring files to prevent recursive ring lifetime hazards.
- Pipe fixed mode rejects `O_CLOEXEC`; errors after partial install must remove both possible fixed slots.
