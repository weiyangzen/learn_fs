# File Research: sources/virtualization/spdk/module/sock/Makefile

Top-level build dispatcher for socket implementation modules.

Key elements:
- Always builds `posix`.
- On Linux, builds `uring` when `CONFIG_URING` is enabled.
- Uses SPDK subdir build infrastructure.

Dependencies:
- Delegates implementation library builds to subdirectories.

Research notes:
- This file selects socket transport implementation modules, separate from the event sock subsystem.
