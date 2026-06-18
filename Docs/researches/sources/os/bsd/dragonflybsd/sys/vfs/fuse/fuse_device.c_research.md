# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_device.c

Implements the `/dev/fuse` character device used by userspace filesystems to receive kernel requests and send replies. It creates/destroys the device and defines open, close, read, write, and kqueue operations.

`fuse_device_open` allocates a zeroed `struct fuse_mount`, initializes its refcount to one, and stores it as per-file devfs private data with `fuse_cdevpriv_dtor`. The actual mount later retrieves this private state by fd.

`fuse_cdevpriv_dtor` calls `fuse_cdevpriv_close`, then frees the mount state if close did not return an error. `fuse_device_close` currently only retrieves private data and logs; actual close teardown is commented out due to a devfs bug.

`fuse_cdevpriv_close` requires the FUSE device to be associated with a mount, then marks the mount dead via `fuse_mount_kill` and wakes kqueue waiters.

`fuse_device_read` is the userspace daemon receive path. It waits on the request queue under `ipc_lock`, handles dead mounts and signals, removes the first pending request, copies it to userspace with `uiomove`, and marks the IPC as sent.

`fuse_device_write` is the userspace daemon reply path. It reads a `fuse_out_header` plus payload into a `fuse_buf`, finds the matching `fuse_ipc` in the reply queue by unique ID, attaches the reply buffer, records `ENOSYS` operations, audits successful reply length with `fuse_audit_length`, marks the IPC replied, and wakes the sleeping kernel requester.

Kqueue support reports readable when the request queue is nonempty and always writable for writes. `fuse_device_init` creates `/dev/fuse` with root/operator permissions; `fuse_device_cleanup` destroys it.

Important dependencies: `fuse_ipc.c` queue semantics, `fuse_mount_kill/free`, `fuse_audit_length`, devfs cdevpriv, kqueue, and `fuse_abi.h` headers.

Notable risks or research hooks: failed length audit returns `EPROTO` from device write but still completes the IPC. If no matching unique reply exists, the reply buffer is freed and `ENOMSG` returned. Device close teardown is intentionally incomplete/commented.
