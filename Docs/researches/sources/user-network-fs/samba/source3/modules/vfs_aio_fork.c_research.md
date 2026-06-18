<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c -->
# sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c

## Purpose
This VFS module simulates asynchronous pread, pwrite, and fsync by dispatching blocking I/O to forked helper children. It avoids in-process blocking while keeping per-request completion integrated with Samba's tevent async VFS interface.

## Important APIs, Types, And Functions
Important structures are `aio_fork_config`, `mmap_area`, `rw_cmd`, `rw_ret`, `aio_child`, and `aio_child_list`. Helpers include shared mmap setup/destruction, file-descriptor passing with `read_fd`/`write_fd`, child cleanup, child creation, idle-child selection, and the child loop. VFS async entry points are `aio_fork_pread_send/recv`, `aio_fork_pwrite_send/recv`, and `aio_fork_fsync_send/recv`, registered by `vfs_aio_fork_init`.

## Control Flow
Connect allocates per-handle config and reads `vfs_aio_fork:erratic_testing_mode`. On async I/O, the module obtains an idle child or forks a new one with a 128 KiB shared mmap area and a socketpair. The parent sends a command and file descriptor to the child. Reads write into shared memory and copy back on completion; writes copy user data into shared memory before dispatch. The parent waits asynchronously for an `rw_ret` packet with result, errno, and duration. Idle children are cleaned after two 30-second cleanup passes without activity.

## State And Persistence
Per-share state includes the child list and cleanup timer. Each child owns a process, socket fd, and shared mmap region. No durable state is persisted; the module only performs underlying file I/O. Child process lifetime is managed by talloc destructors and timed cleanup.

## Dependencies And Integration Points
The module depends on Unix fd passing via `sendmsg`/`recvmsg`, `mmap`, `fork`, Samba tevent, async socket helpers, sys read/write wrappers, profiling timestamps, and VFS async hooks. It closes inherited pathref fds in children to avoid holding system-level share modes.

## Risks
Requests larger than 128 KiB fail with `EINVAL`. Child death or malformed packets surface as async errors and may destroy the child. File descriptor passing support is required at compile time. Shared-memory copying means callers must respect async buffer lifetimes. Forked children inherit process state, so careful fd cleanup is needed to avoid share-mode side effects.

## Test Signals
Tests should exercise async read/write/fsync success, append write path, oversized request rejection, child reuse and cleanup, child failure recovery, errno propagation, duration reporting, and optional erratic delay mode. Integration tests should verify no share-mode leakage from inherited fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_aio_fork.c -->
