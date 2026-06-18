# File Research: sources/os/bsd/openbsd-src/sys/sys/ucred.h

Defines kernel credentials. `struct ucred` contains a refcount and copied credential fields: effective/real/saved uid and gid plus supplementary groups. `cr_startcopy` marks the first field copied by `crset`.

`struct xucred` is the userspace/syscall credential shape. Kernel APIs allocate, hold, copy, duplicate, set, free, convert from `xucred`, and check superuser privileges. `NOCRED` and `FSCRED` are sentinel credential pointers.
