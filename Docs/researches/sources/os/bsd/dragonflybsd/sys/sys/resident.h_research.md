# File Research: sources/os/bsd/dragonflybsd/sys/sys/resident.h

Resident executable support syscall declarations and sysctl export structure.

Key responsibilities:
- Declares userland `exec_sys_register()` and `exec_sys_unregister()` when not building the kernel.
- Defines `struct xresident`, exported via sysctl `vm.resident`, containing resident entry address, resident id, file path, and file stat data.

Important behavior:
- `res_file` is sized to `MAXPATHLEN`.
- The structure embeds `struct stat`, preserving file metadata for userland inspection.

Dependencies:
- Includes `sys/types.h`, `sys/param.h`, and `sys/stat.h`.

Notable risks:
- `xresident` is a sysctl ABI structure; field layout and embedded `struct stat` compatibility matter.
- Entry address is exposed as `intptr_t`, so consumers should treat it as address-sized data.
