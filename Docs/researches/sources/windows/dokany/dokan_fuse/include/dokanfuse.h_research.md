# File Research: sources/windows/dokany/dokan_fuse/include/dokanfuse.h

Private C++ definitions for the Dokan FUSE compatibility layer.

Key contents:
- `FUSE_THREAD_COUNT` and `DOKAN_DLL` naming macro.
- `printf` format macros for `DWORD`/`ULONG` across LP64 and LLP64 environments.
- `fuse_config` storing parsed FUSE/Dokan options: masks, names, debug, mount manager, read-only, timeout, removable/network flags, allocation unit, sector size, and max read.
- `fuse_session` and `fuse_chan`.
- `fuse_chan` dynamically loads Dokan DLL functions: `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanUnmount`, `DokanRemoveMountPoint`.
- `fuse` object storing loop state, channel/session, config, operations, and user data.

Role:
- Holds the bridge’s runtime state and dynamic linking boundary to `dokan*.dll`.
