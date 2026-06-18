# File Research: sources/teaching/minix/minix/servers/vfs/comm.c

This file implements worker-thread communication with filesystem servers, block drivers, and VM.

Key functions:
- `sendmsg`: low-level async send with VFS transaction ID tagging.
- `send_work`: tries to drain queued filesystem-server requests.
- `fs_cancel`: cancels queued requests for a mount.
- `fs_sendmore`: sends queued work if the mounted FS has capacity.
- `drv_sendrec`: serialized send/receive-style request to a device driver.
- `fs_sendrec`: send/receive-style request to a mounted filesystem, with queueing and worker suspension.
- `vm_sendrec`: send/receive-style request to VM.
- `vm_vfs_procctl_handlemem`: sends VM memory-handling requests.
- `queuemsg`: appends the current worker to a mount’s request queue.

Important behavior:
- Filesystem requests carry transaction IDs based on worker thread IDs.
- Each mounted filesystem has `c_cur_reqs`, `c_max_reqs`, and a request queue.
- FS callbacks are withheld while `VMNT_CALLBACK` is set.
- `drv_sendrec` locks the `dmap` entry and records the servicing worker thread.
- The CTTY pseudo-major is explicitly rejected for block-driver send/receive.
- `fs_sendrec` converts accidental `ERESTART` from FS replies into `EIO`.
