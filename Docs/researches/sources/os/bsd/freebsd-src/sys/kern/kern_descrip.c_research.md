# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_descrip.c

Read completely: 5703 lines.

## Purpose
Implements FreeBSD's core file descriptor, open-file, process directory, descriptor capability, and descriptor-reporting machinery.

## Main Elements
- Maintains per-process `struct filedesc` descriptor tables using descriptor arrays plus bitmaps, with small static `NDFILE` storage and dynamic growth through `fdgrowtable()`.
- Implements descriptor syscalls and helpers: `getdtablesize`, `dup`, `dup2`, `fcntl`, `close`, `close_range`, `fstat`, `fpathconf`, and `flock`.
- Handles descriptor allocation/install/free paths via `fdalloc()`, `falloc_caps()`, `_falloc_noinstall()`, `finstall_refed()`, `_finstall()`, `fdfree()`, `closefp()`, `closef()`, and `_fdrop()`.
- Supports Capsicum descriptor rights through `struct filecaps`, including copying, moving, validation, ioctl/fcntl rights, and lockless sequence-counter validation.
- Provides lockless and locked file lookup paths: `fget_unlocked_seq()`, `fget_unlocked_flags()`, `fget_cap()`, `fget_mmap()`, `fget_fcntl()`, `fgetvp_*()`, and remote-process variants.
- Manages process descriptor table sharing and copying for fork/rfork/exec through `fdinit()`, `fdcopy()`, `fdshare()`, `fdunshare()`, `fdescfree()`, `fdcloseexec()`, and POSIX lock cleanup for shared descriptor tables.
- Manages process working/root/jail/alternate directory state through `struct pwddesc` and `struct pwd`, including `pwd_chdir()`, `pwd_chroot()`, `pwd_chroot_chdir()`, `pwd_altroot()`, `pwd_ensure_dirs()`, and `mountcheckdirs()`.
- Implements setugid descriptor safety, standard fd repair through `/dev/null`, and chroot open-directory refusal policy.
- Provides async I/O ownership helpers `fsetown()`, `fgetown()`, `funsetown()`, and `funsetownlst()` around `sigio`.
- Exports descriptor state for sysctl/procstat via `kern_proc_filedesc_out()`, `kern_proc_cwd_out()`, `sysctl_kern_file`, and kinfo packing.
- Defines fallback `badfileops`, `path_fileops` for `O_PATH`-style vnode descriptors, invalid file operation helpers, DDB file inspectors, global maxfiles sysctls, UMA zones, and `/dev/fd/{0,1,2}` alias device setup.

## Dependencies And Integration
Tightly integrated with VFS/vnodes, Capsicum, proc/session locking, kqueue, audit, ktrace, jails, RACCT, MAC-visible consumers through vnode operations, sysctl, DDB, UMA, and device aliases for `/dev/fd`, `stdin`, `stdout`, and `stderr`.

## Risk Notes
This is high-risk shared kernel infrastructure. Correctness depends on precise lock ordering, descriptor sequence counters, reference-count acquisition from lockless paths, file table growth lifetime rules, capability-right validation, close/drop races, POSIX advisory lock cleanup across shared descriptor tables, and root/current-directory vnode reference handling.
