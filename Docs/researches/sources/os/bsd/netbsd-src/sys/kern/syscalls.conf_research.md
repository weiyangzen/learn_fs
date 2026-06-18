# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls.conf

Configuration input for NetBSD syscall generation.

Key settings:
- Generates syscall names to `syscalls.c`.
- Generates syscall numbers to `../sys/syscall.h`.
- Generates syscall switch table to `init_sysent.c`.
- Generates syscall argument header to `../sys/syscallargs.h`.
- Adds extra argument-header includes for `idtype.h`, `mount.h`, `sched.h`, `acl.h`, and `socket.h`.
- Generates autoload data to `syscalls_autoload.c`.
- Generates rump syscall outputs and map files.
- Lists supported compatibility option prefixes from `compat_09` through `compat_110`.
- Sets `switchname="sysent"`, `namesname="syscallnames"`, `constprefix="SYS_"`, `emulname="netbsd"`, and `nsysent=512`.

Research notes:
- This file controls how `makesyscalls.sh` emits the generated syscall artifacts used by this group.
