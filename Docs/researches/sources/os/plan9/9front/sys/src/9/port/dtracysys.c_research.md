# File Research: sources/os/plan9/9front/sys/src/9/port/dtracysys.c

Provides the `dtracy` syscall provider. It wraps entries in `systab[]` with generated `WRAP0` through `WRAP5` functions that copy syscall arguments from a `va_list`, trigger `sys:<name>:entry`, invoke the original syscall, place the return value in `arg[9]`, and trigger `sys:<name>:return`.

`wraptab[]` maps syscall numbers to wrappers for common Plan 9 syscalls including bind, open, read, write, mount, stat, wstat, pread, pwrite, semacquire, seek, and nsec. `sysprovide` creates entry/return probes for every valid syscall name in `sysctab`, normalizing uppercase names and special-casing `SYSR1`.

`sysenable` and `sysdisable` swap `systab[i]` with `wraptab[i]` when total enabled probes transitions to or from zero. This pointer-swap scheme is compact but assumes wrapper coverage for enabled syscall indices.
