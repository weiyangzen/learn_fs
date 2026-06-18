# File Research: sources/os/plan9/9front/sys/src/9/mt7688/syscall.c

This file provides MT7688 syscall, note, fork, and exec register handling. `syscall(Ureg*)` is called directly from assembly for system-call traps, enters kernel context, dispatches `dosyscall` using `r1` as syscall number and user stack as arguments, advances PC on success, delivers notifications, handles delayed scheduling, exits kernel context, and restores `EXL` in status.

It also implements FP note-state markers `fpunotify` and `fpunoted`, while `notefpsave` returns nil for this emulated/stubbed FP setup. `notify` builds a user stack frame containing a copied `Ureg` and error string, then redirects PC to the user notify handler. `noted` restores registers and supports `NCONT`, `NRSTR`, and `NSAVE`.

`forkchild` creates a child kernel return frame so the child resumes from `forkret` with return value 0. `execregs` sets initial user stack and PC for `exec`, with PC set to `entry - 4` because the syscall return path advances it.

Filesystem relevance is direct: all filesystem syscalls on this port traverse this file, including open/read/write/mount/stat operations handled by the portable syscall layer.

Notable risks: syscall argument ABI is MIPS/Plan 9 specific; `execregs` relies on the syscall path’s PC advance; note-frame validation is critical for user-controlled register restoration.
