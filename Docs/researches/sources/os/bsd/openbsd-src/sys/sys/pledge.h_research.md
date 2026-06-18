# File Research: sources/os/bsd/openbsd-src/sys/sys/pledge.h

Defines pledge promise bitmasks, optional promise-name table, and kernel enforcement hooks.

Key contents:
- Promise bits for filesystem path access, stdio, DNS, networking, flock, Unix sockets, identity changes, tape, process control, time setting, file attributes, executable mappings, tty, fd passing, exec, routing, multicast, vm/process info, disklabel, pf, audio/video, device-path, drm, vmm, chown, bpf, unveil, and error mode.
- `PLEDGE_ALWAYS` and `PLEDGE_USERSET`.
- Optional `pledgenames[]` table under `PLEDGENAMES`.

Kernel APIs:
- `pledge_syscall`, `pledge_fail`, `pledge_namei`.
- Specific checks for fd passing, sysctl, chown, adjtime, send, socket options, socket creation, ioctl families, flock, fcntl, swapctl, kill, and `PROT_EXEC`.

Risk notes:
- This header is a security policy contract; new syscalls/ioctls must map to the correct promise bits.
