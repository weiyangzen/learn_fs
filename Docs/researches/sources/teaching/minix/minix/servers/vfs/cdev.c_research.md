# File Research: sources/teaching/minix/minix/servers/vfs/cdev.c

This file handles VFS-side character device operations, including suspendable I/O and select.

Key functions:
- `cdev_map`: maps `/dev/tty` to the caller’s controlling terminal and bounds-checks majors.
- `cdev_get`: resolves a character device to a valid `dmap` entry and minor number.
- `cdev_clone`: creates a temporary PFS device node for cloned character devices.
- `cdev_open` / `cdev_close`: synchronous open/close wrappers around `cdev_opcl`.
- `cdev_io`: initiates read, write, or ioctl and suspends the calling process.
- `cdev_select`: sends select requests without controlling-terminal remapping.
- `cdev_cancel`: sends cancel and waits for cancellation/completion.
- `cdev_reply`: dispatches normal and select replies.
- `cdev_generic_reply`: resumes waiting worker threads or revives suspended processes.

Important behavior:
- Open/close block the worker thread; read/write/ioctl may suspend the process and free the worker.
- Controlling TTY rules are enforced at open time with `O_NOCTTY`.
- `/dev/tty` itself is not actually opened/closed in the driver.
- Clone opens replace the file descriptor’s vnode with a PFS-created device node.
- Character I/O uses grants to expose user buffers to drivers.
- `TIOCSCTTY` directly updates `fp_tty` for TTY/PTTY majors before driver success is known, called out by a FIXME.
- Reply handling converts certain `EINTR`/`EAGAIN` cases for historical driver behavior.
