# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nvmecontrol.c

Purpose: Main program entry point and common helper implementation for `nvmecontrol`.

Key behavior:
- Provides hex printing helpers for byte and dword-oriented output.
- Implements `read_controller_data()`, `read_namespace_data()`, and `read_active_namespaces()` using `NVME_PASSTHROUGH_CMD` identify commands, then host-endian swaps returned data.
- Implements `open_dev()`, resolving bare device names under `/dev/`.
- Implements `get_nsid()` via `NVME_GET_NSID`.
- `main()` initializes command registration, loads modules from `/lib/nvmecontrol` and `${LOCALBASE}/lib/nvmecontrol`, then dispatches parsed commands.

Dependencies:
- `comnd.h` via `nvmecontrol.h`.
- `libutil` for `getlocalbase()`.
- FreeBSD NVMe ioctl ABI.

Research notes:
- Dynamic plugin loading is central to the command architecture.
- Helper functions return `errno`/`EIO` rather than exiting, except `open_dev()` can exit depending on caller policy.
