# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_ipc.c

Implements FUSE IPC object allocation, request construction, queueing, waiting, timeout handling, and cleanup. It uses two malloc types and an objcache for `struct fuse_ipc`.

`fuse_buf_alloc` and `fuse_buf_free` manage variable-sized request/reply buffers. `fuse_ipc_get` allocates and zeroes an IPC object, initializes refcount, stores mount pointer, assigns a unique ID with `atomic_fetchadd_long`, allocates the input buffer including `struct fuse_in_header`, and leaves reply empty.

`fuse_ipc_put` releases an IPC object, freeing request and reply buffers and returning the object to the cache when the refcount reaches zero.

`fuse_ipc_fill` writes the FUSE input header using opcode, inode, unique ID, credentials, group ID, and pid, then returns the request payload pointer.

`fuse_ipc_remove` removes an IPC object from either request or reply queues under `ipc_lock`, waking waiters if it removes an unsent request.

`fuse_ipc_wait` waits for a reply. It detects dead mounts, sleeps with a five-second timeout, retries timeouts up to six times, removes timed-out or interrupted IPCs, marks them replied, and returns `ETIMEDOUT`, signal errors, or `ENOTCONN` as appropriate.

`fuse_ipc_wait_sent` is used for no-reply operations such as `FUSE_FORGET`; it waits only until the daemon has read the request from `/dev/fuse`.

`fuse_ipc_tx` queues an IPC on both reply and request queues, wakes `/dev/fuse` readers and kqueue waiters, waits for a reply, converts negative FUSE errors to positive errno values, and leaves successful IPC ownership to the caller for result extraction and `fuse_ipc_put`.

`fuse_ipc_tx_noreply` queues only on the request queue and waits until sent; the caller later drops the IPC on success.

Important dependencies: request/reply queue consumers in `fuse_device.c`, ABI headers, mount dead-state helpers, and DragonFly sleep/wakeup primitives.

Notable risks or research hooks: timeout policy is fixed at repeated five-second sleeps. `fuse_ipc_tx` returns without freeing the IPC on success so callers must call `fuse_ipc_put`; error paths free internally.
