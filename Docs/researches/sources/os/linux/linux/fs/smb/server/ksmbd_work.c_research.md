# File Research: sources/os/linux/linux/fs/smb/server/ksmbd_work.c

This file manages per-request `struct ksmbd_work` allocation, freeing, queueing, and response iovec construction.

Main behavior:
- Creates a `ksmbd_work_cache` slab for work objects.
- Creates the `ksmbd-io` percpu workqueue.
- `ksmbd_alloc_work_struct()` initializes compound FIDs, request/async/file list nodes, aux read list, and an initial 4-entry iovec array.
- `ksmbd_free_work_struct()` releases response/request buffers, transform buffer, iovec storage, auxiliary read buffers, async ID, and the slab object.
- `ksmbd_queue_work()` queues work to the KSMBD I/O workqueue.
- `ksmbd_iov_pin_rsp()` and `ksmbd_iov_pin_rsp_read()` append response buffers to the work iovec array and maintain the RFC1001/1002 length in iov[0].
- `allocate_interim_rsp_buf()` allocates a small response buffer for interim replies.

The code owns response vector bookkeeping used later by signing/encryption and transport write paths.
