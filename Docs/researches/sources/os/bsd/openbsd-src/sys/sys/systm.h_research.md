# File Research: sources/os/bsd/openbsd-src/sys/sys/systm.h

Core kernel global declarations, syscall table shape, copy/print/memory helpers, sleep/wakeup APIs, hooks, network lock macros, and boot/root-device declarations.

This header declares global kernel state such as `securelevel`, panic/version strings, hardware identity, CPU/device counts, physical memory, dump/root/swap devices, root and swap vnodes, and the current process macro. It defines `struct sysent`, syscall handler type, `SY_NOLOCK`, endian-aware `SCARG()`, and optional syscall-debug declarations.

The function surface includes generic stubs, hash allocation, panic/assert/printf/uprintf/snprintf, spl assertions, table-full reporting, kernel/user copy helpers, memory routines, randomness, clock/profiling hooks, sleep queues, condition variables, wakeup/tsleep/msleep/rwsleep variants, watchdog hooks, startup hooks, `uiomove()`, network lock/assert macros, setjmp/longjmp, console/CPU configuration, disk/root mount selection, builtin memory macro mappings, DDB hooks, boot config hooks, and global kernel lock macros.

Filesystem/storage relevance: foundational. It declares root and swap device/vnode state, dump-device state, `diskconf()`, `mountroot`, `nfs_mountroot()`, `dk_mountroot()`, `uiomove()`, copyin/copyout, sleep/wakeup, securelevel policy affecting raw disks, and kernel lock/network lock primitives used by VFS, storage, and socket code.
