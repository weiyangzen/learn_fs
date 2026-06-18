# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reset.c

Purpose: Implements `nvmecontrol reset`.

Key behavior:
- Registers top-level `reset`.
- Opens a controller or namespace device for write.
- If a namespace is supplied, resolves and reopens the owning controller.
- Issues `NVME_RESET_CONTROLLER`.

Dependencies:
- `open_dev()` and `get_nsid()`.
- FreeBSD `NVME_RESET_CONTROLLER` ioctl.

Research notes:
- This is a thin controller-level operation wrapper with no extra confirmation prompt.
