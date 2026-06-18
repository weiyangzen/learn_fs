# File Research: sources/os/bsd/freebsd-src/sys/sys/sysproto.h

## Scope

This automatically generated header declares FreeBSD syscall argument structures, syscall implementation prototypes, compatibility syscall surfaces, and audit event mappings. It is generated from the syscall master description and is consumed by syscall implementations, syscall table generation, ABI compatibility code, and audit metadata setup.

## APIs And Generated Surfaces

- Defines padding helpers `PAD_`, `PADL_`, and `PADR_` so syscall argument structures preserve register-sized argument slots across little-endian and big-endian targets.
- Includes required public kernel/user ABI types from `sys/types.h`, `sys/signal.h`, `sys/cpuset.h`, `sys/domainset.h`, `_ffcounter`, `_semaphore`, `ucontext`, `wait`, and BSM audit events.
- Declares 495 syscall argument structures and 495 matching syscall implementation prototypes.
- Declares argument/prototype pairs for core process, file, VFS, VM, socket, time, scheduler, security, audit, IPC, POSIX AIO, kqueue, jail, Capsicum, cpuset/domainset, shared memory, timerfd, inotify, process descriptor, kexec, and extended error/sysctl facilities.
- Defines 495 `SYS_AUE_*` macros that map syscall names to BSM audit event constants, including `AUE_NULL` for unaudited or non-security-relevant operations.
- Undefines the internal padding helpers before leaving the header.

## Syscall Families Covered

- Process and credential operations: exit/fork/vfork/rfork, wait variants, get/set uid/gid/groups, setresuid/setresgid, process groups/sessions, `procctl`, `setcred`, and process descriptor calls.
- File and VFS operations: open/close/read/write, vector and positioned I/O, stat/statfs families, link/unlink/rename variants, mkdir/rmdir/mknod/mkfifo, chmod/chown/chflags, pathconf, filesystem handles, `copy_file_range`, `fspacectl`, `funlinkat`, and `close_range`.
- Filesystem-adjacent controls: mount/unmount/nmount, `quotactl`, NFS service/file-handle calls, extended attributes, ACL calls, MAC label calls, and shared-memory object calls.
- IPC and synchronization: SysV sem/msg/shm, POSIX semaphores, message queues, umtx, timerfd, and memory barriers.
- Networking: sockets, bind/connect/accept/listen/shutdown, send/receive variants, socketpair, `bindat`, `connectat`, SCTP compatibility entry points, and RPC TLS syscall hook.
- VM and memory: break, mmap/munmap/mprotect/madvise/mincore/minherit, mlock/munlock, and memory-locking AIO.
- Time and timers: get/set time of day, adjtime, NTP calls, POSIX clocks/timers, nanosleep variants, ffclock APIs, and CPU clock lookup.
- Security and policy: Capsicum, audit/auditon/auditctl, jail operations, login class, resource controls, MAC framework syscalls, and `issetugid`.
- System management: reboot, ktrace/utrace, sysctl/sysctlbyname, kernel environment, module/KLD calls, UUID generation, `getrandom`, `kcmp`, `exterrctl`, and `__specialfd`.

## Compatibility Blocks

- `COMPAT_43` provides old 4.3BSD syscall argument/prototype forms for legacy stat, signal, socket, mmap, truncate, hostname, rlimit, and directory APIs.
- `COMPAT_FREEBSD4` covers old statfs/domain/uname/sendfile/signal-context variants.
- `COMPAT_FREEBSD6` covers old offset-padding and old AIO/sigevent layouts for pread/pwrite/mmap/lseek/truncate/ftruncate and AIO list operations.
- `COMPAT_FREEBSD7` covers old SysV IPC control layouts.
- `COMPAT_FREEBSD10` covers old pipe and umtx lock/unlock entry points.
- `COMPAT_FREEBSD11` covers old device number, stat, dirent, kevent, statfs, fstatat, and mknodat layouts.
- `COMPAT_FREEBSD12`, `COMPAT_FREEBSD13`, and `COMPAT_FREEBSD14` cover renamed or layout-changed shm, closefrom, swapoff, and groups syscalls.

## Control Flow And Integration

- Each syscall implementation receives `struct thread *` plus a pointer to its generated argument structure.
- The argument structures are the ABI boundary between machine-dependent syscall argument fetch code and machine-independent syscall bodies.
- Generated `SYS_AUE_*` values are consumed by `sysent` initializers so audit classification follows the same syscall source as the prototypes.
- Compatibility blocks compile only when the corresponding ABI support is enabled, allowing old user binaries to keep their historical argument layouts.

## Dependencies

- Depends on generated syscall-number and syscall-table machinery outside this header.
- Uses many forward-declared or externally defined ABI structures such as file handles, ACLs, MAC labels, AIO control blocks, message queue attributes, jail descriptors, resource-control buffers, stat/statfs variants, and compatibility-only legacy structures.
- Integrates with `sysent.h` through `SYS_AUE_*` names and `struct *_args` names used by syscall table initializers.

## Risks And Invariants

- This file is generated; manual edits would be overwritten and can desynchronize prototypes, argument layouts, audit mappings, and syscall tables.
- Padding macros are ABI-critical. Incorrect padding changes how register-sized syscall arguments are interpreted on mixed-width or different-endian targets.
- The count and names of arg structures, prototypes, and audit mappings must remain synchronized; in this version each count is 495.
- Compatibility layouts are intentionally old and sometimes awkward; replacing them with native structures would break legacy binaries.
- Audit mappings are security-sensitive because they determine which audit event is recorded for each syscall.
