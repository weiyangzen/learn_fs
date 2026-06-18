# File Research: sources/os/linux/linux/fs/fcntl.c

## Purpose
Implements Linux `fcntl` and `fcntl64` system call handling, file-owner management for async notifications, read/write lifetime hints, lease/delegation command dispatch, compat flock conversion, and fasync signal delivery infrastructure.

## Main Responsibilities
- Implements `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, dupfd commands, lock commands, owner/signal commands, leases, dnotify, pipe sizing, memfd seals, write hints, and delegations.
- Manages `struct fown_struct` allocation, ownership, credentials, pid references, and release.
- Sends `SIGIO`/custom async I/O signals and `SIGURG`.
- Maintains fasync lists used by drivers and lease code.
- Provides compat syscall handling for 32-bit userspace flock structures.

## Key Interfaces
- `setfl()`: validates and updates mutable file status flags.
- `file_f_owner_allocate()` / `file_f_owner_release()`: lifecycle for per-file owner state.
- `__f_setown()`, `f_setown()`, `f_delown()`, `f_getown()`: legacy owner APIs.
- `f_setown_ex()` / `f_getown_ex()`: extended owner APIs with PID/TGID/PGRP selection.
- `do_fcntl()`: central command dispatcher.
- `SYSCALL_DEFINE3(fcntl)` and `fcntl64`: syscall entry points.
- `do_compat_fcntl64()` and compat syscalls: compat lock structure handling.
- `send_sigio()` / `send_sigurg()`: notification delivery.
- `fasync_helper()`, `fasync_insert_entry()`, `fasync_remove_entry()`, `kill_fasync()`: fasync list management.
- `fcntl_init()`: initializes the fasync slab cache.

## Important Behavior
`setfl()` allows only `SETFL_MASK` bits to change, prevents clearing append on append-only writable files, restricts `O_NOATIME` to owner/capable callers, maps `O_NDELAY` to `O_NONBLOCK` where needed, validates `O_DIRECT`, and delegates filesystem-specific validation through `check_flags`.

File ownership stores pid, pid type, uid, and euid under `f_owner->lock`. Signals are permission-checked against saved owner credentials and LSM hooks before delivery.

`do_fcntl()` first handles generic fd/status commands, then locking via `fcntl_getlk`/`fcntl_setlk`, owner commands, leases, dnotify, pipe, memfd, write-hint, and delegation commands. `FMODE_PATH` descriptors are restricted to a small safe command set by `check_fcntl_cmd()`.

Compat handling converts `compat_flock` and `compat_flock64`, maps 64-bit lock commands, and guards overflow for 32-bit `struct flock` results.

Fasync list updates hold both `filp->f_lock` and global `fasync_lock`; removal uses RCU freeing. `kill_fasync()` traverses under RCU and sends signals through the file owner if present.

## Dependencies
Calls into VFS file table helpers, file locking, leases/delegations, dnotify, pipe, memfd, LSM hooks, pid namespaces, credentials, compat/uaccess helpers, and polling signal code.

## Research Notes
This file is not FAT-specific; it is generic VFS/syscall infrastructure included in the same research group. It interacts with FAT indirectly because FAT file and directory operations expose `.setlease = generic_setlease`, and all open FAT files are subject to these generic fcntl paths.
