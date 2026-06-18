# File Research: sources/os/linux/linux/fs/eventfd.c

## Purpose
Implements Linux `eventfd`, an anonymous-file counter object used for userspace and kernel event notification through read, write, poll, and exported context APIs.

## Main Elements
- Core state: `struct eventfd_ctx` holds a kref, waitqueue, 64-bit counter, flags, and proc-visible ID.
- Kernel signaling: `eventfd_signal_mask()` increments the counter up to `ULLONG_MAX`, wakes poll waiters, supports an extra poll mask, and guards against recursive eventfd wakeups with `current->in_eventfd`.
- Lifetime management: `eventfd_ctx_put()`, `eventfd_free()`, and `eventfd_free_ctx()` handle kref release and IDA ID cleanup.
- File operations: `eventfd_poll()` reports readable, writable, and overflow/error states; `eventfd_read()` blocks or returns `-EAGAIN` until count is nonzero, then consumes either one semaphore unit or the whole count; `eventfd_write()` validates a u64 write and blocks until the counter can accept it.
- Atomic waitqueue removal: `eventfd_ctx_remove_wait_queue()` removes an external wait entry while reading/resetting the counter under the waitqueue lock.
- Proc fdinfo: `eventfd_show_fdinfo()` reports count, ID, and semaphore mode.
- External acquisition APIs: `eventfd_fget()`, `eventfd_ctx_fdget()`, and `eventfd_ctx_fileget()` validate eventfd files and take file/context references.
- Syscalls: `eventfd2` and legacy `eventfd` create anonymous inode files through `do_eventfd()`, validate flags, initialize context, allocate IDs, and publish descriptors.

## Dependencies And Integration
Integrates with anonymous inodes, VFS file operations, poll/epoll waitqueues, exported kernel notification users, proc fdinfo, IDA allocation, krefs, and user-copy/iov-iter helpers.

## Risk Notes
All counter updates occur under `ctx->wqh.lock`, and the poll path depends on ordering through `poll_wait()` waitqueue locking to avoid missed wakeups. Recursive wakeups can deadlock or overflow stacks, so `current->in_eventfd` is used around wakeup paths. Writes must reject `ULLONG_MAX` and reserve one count value so overflow can be signaled as `EPOLLERR`.
