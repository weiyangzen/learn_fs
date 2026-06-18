# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_mib.c

## Purpose

`kern_mib.c` defines top-level sysctl namespaces and machine-independent kernel, hardware, user, security, compatibility, and debug MIB entries for DragonFlyBSD.

## Main Responsibilities

- Creates root sysctl nodes such as `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `p1003_1b`, `lwkt`, `compat`, and `security`.
- Exposes kernel identity, release, version, OS revision/date, static TLS extra space, process limits, POSIX constants, bootfile, CPU count, byte order, page size, platform, and architecture.
- Exposes hostname, securelevel, NIS domain name, and host ID.
- Publishes placeholder POSIX user-level constants expected by libc/userland interfaces.
- Publishes `debug.sizeof` entries for `vnode`, `proc`, and `cdev`.
- Creates the `kern.features` node for feature flags registered elsewhere.

## Custom Handlers

`sysctl_hostname()` uses `CTLFLAG_NOLOCK` to avoid per-OID locking on read and upgrades the sysctl lock only for writes. In jailed processes it reads or writes the prison hostname and enforces `PRISON_CAP_SYS_SET_HOSTNAME` for writes.

`sysctl_kern_securelvl()` allows securelevel to increase but rejects attempts to lower it with `EPERM`.

## Integration Notes

The file exports globals used elsewhere in this group: `kernelname`, `securelevel`, `kernel_mem_readonly`, `hostname`, `domainname`, and `hostid`. `kern_lockf.c` uses `maxposixlocksperuid`, while `kern_memio.c` and `kern_linker.c` consult `securelevel` and `kernel_mem_readonly`.
