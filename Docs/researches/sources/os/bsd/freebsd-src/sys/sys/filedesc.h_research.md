# File Research: sources/os/bsd/freebsd-src/sys/sys/filedesc.h

## Purpose
Defines process file descriptor tables, per-descriptor Capsicum rights, current/root directory state, descriptor locks, and kernel descriptor allocation/lookup APIs.

## Main Interfaces
- `struct filecaps`: rights, allowed ioctls, allowed fcntls.
- `struct filedescent`: file pointer, caps, per-fd flags, sequence counter.
- `struct fdescenttbl`: allocated descriptor table.
- `struct pwd`: copy-on-write current/root/jail/ABI root directories.
- `struct pwddesc`: locked pointer to `pwd` plus umask/refcount.
- `struct filedesc`: open files, free bitmap, refs, sx lock, kqueue list, leader hold state.
- `struct filedesc_to_leader`: POSIX lock ownership tracking for shared descriptor tables.
- Per-fd flags: `UF_EXCLOSE`, `UF_RESOLVE_BENEATH`, `UF_FOCLOSE`.
- Lock macros for `pwddesc` and `filedesc`.
- Dup modes and flags: `FDDUP_*`, `FDDUP_FLAG_CLOEXEC`, `FDDUP_FLAG_CLOFORK`.
- Filecap helpers: `filecaps_init`, `copy`, `move`, `free`.
- Descriptor lifecycle APIs: `falloc*`, `finstall*`, `fdalloc*`, `fdclose`, `fdcloseexec`, `fdcopy`, `fdunshare`, `fdescfree`, `fdinit`, `fdshare`.
- Lookup APIs: `fget_cap*`, `fget_unlocked*`, `fget_only_user`, `fget_noref_unlocked`, `fget_noref`, `fdeget_noref`.
- Directory state APIs: `pdcopy`, `pdinit`, `pdshare`, `pdunshare`, `pwd_*`, `pwd_hold*`, `pwd_drop`, `pwd_set`.

## Dependencies And Integration
Includes Capsicum rights, kqueue structures, locks, sequence counters, SMR primitives, and machine limits. It coordinates with `file.h`, VFS namei/path lookup, process lifecycle, fork/exec behavior, and capability mode.

## Risk Notes
Descriptor lookup has multiple safety modes: locked, unlocked with ref, no-ref, SMR, and only-user fast paths. Callers must choose the correct one. Capability sequence counters guard against races between file pointer and rights changes.
