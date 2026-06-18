# File Research: sources/teaching/minix/minix/fs/procfs/inc.h

`inc.h` is the umbrella include for ProcFS. It pulls in MINIX driver, parameter, sysctl, sysinfo, VTreeFS, and ProcFS interfaces, plus assertions and architecture/kernel/VFS internal headers needed for process and device-map data.

It then includes the local ProcFS headers: constants, types, prototypes, and globals. Most ProcFS implementation files include only `inc.h` to obtain the shared service environment.
