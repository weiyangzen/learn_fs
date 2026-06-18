# File Research: sources/os/bsd/netbsd-src/sys/sys/shm.h

Read completely: 205 lines.

This header defines System V shared memory ABI and kernel hooks. Public pieces include attach flags, `SHMLBA`, `shmatt_t`, `struct shmid_ds`, NetBSD lock/unlock command constants, compatibility permission aliases, `struct shminfo`, sysctl export structs, and prototypes for `shmat`, `shmctl`, `shmdt`, and `shmget`.

Kernel code gets internal flags for segment state, global `shminfo`, `shmsegs`, and `shm_nused`, lifecycle functions, fork/exit hooks, `shmctl1`, permission lookup by index, UVM hook pointers, and a sysctl fill macro.

Risks: `SHMLBA` resolves differently in kernel versus userland, with userland calling internal `__sysconf(28)`. Segment removal/linger/wired flags are kernel-only and must be synchronized with attach/detach lifetime.
