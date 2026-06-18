# File Research: sources/os/bsd/openbsd-src/sys/sys/kcov.h

This header defines the kernel coverage device ioctl ABI and kernel hooks.

Key definitions:
- Ioctls: `KIOSETBUFSIZE`, `KIOENABLE`, `KIODISABLE`, `KIOREMOTEATTACH`.
- Coverage modes: `KCOV_MODE_NONE`, `KCOV_MODE_TRACE_PC`, `KCOV_MODE_TRACE_CMP`.
- Remote subsystem id: `KCOV_REMOTE_COMMON`.
- `struct kio_remote_attach`.

Kernel APIs/globals:
- `kcov_cold`
- `kcov_exit`
- `kcov_vnode`
- `kcov_remote_register`
- `kcov_remote_unregister`
- `kcov_remote_enter`
- `kcov_remote_leave`

Risk notes:
- Coverage buffers are user-controlled through ioctl, so buffer sizing and mmap/device access must be carefully bounded in implementation.
- Remote coverage requires subsystem/id registration discipline to avoid attributing events to the wrong context.
