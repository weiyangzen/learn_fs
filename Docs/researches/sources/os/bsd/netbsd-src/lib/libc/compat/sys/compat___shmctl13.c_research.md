# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___shmctl13.c

Read completely: 68 lines.

This implements old `__shmctl13` for SysV shared memory. It converts `shmid_ds13` to native for `IPC_SET`, calls `__shmctl50`, and converts native output to `shmid_ds13` for `IPC_STAT`.

Security/reliability notes: direct ABI conversion wrapper; old timestamp and size fields can be narrower than current native fields.
