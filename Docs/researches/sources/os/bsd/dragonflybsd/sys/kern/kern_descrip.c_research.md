# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_descrip.c

## Purpose

Implements DragonFlyBSD file descriptor tables, open file object lifetime, descriptor duplication/close/fcntl syscalls, descriptor caching, revocation, `/dev/fd`, file-table sysctls, and fallback file operations.

This is one of the core VFS-facing process I/O files: it maps integer file descriptors to `struct file`, dispatches file operations, and controls close semantics that release vnode/socket/pipe resources.

## Key Responsibilities

- Manages `struct filedesc` tables and `struct file` references.
- Allocates descriptor numbers efficiently using an in-place binary-tree allocation count in `fd_files[].allocated`.
- Maintains per-thread descriptor caches (`td_fdcache`) to speed up repeated fd-to-file lookups.
- Implements syscalls and kernel helpers for `dup`, `dup2`, `fcntl`, `close`, `closefrom`, `shutdown`, `fstat`, `fpathconf`, and `flock`.
- Implements POSIX/BSD advisory-lock cleanup during close, exec, fork, and descriptor-table release.
- Tracks global open files through hashed file lists.
- Handles file pointer revocation for revoked vnodes/devices.
- Initializes `/dev/fd/N`, `/dev/stdin`, `/dev/stdout`, and `/dev/stderr`.
- Exposes file-table information and tunables via sysctls.

## Major Data Structures and State

- `filelist_heads[NFILELIST_HEADS]`: hashed global lists of all live `struct file` objects, each protected by a spinlock.
- `nfiles`: global open file count.
- `revoke_token`: serializes revocation against descriptor externalization paths.
- `struct filedesc`: per-process descriptor table with spinlock, current/root/jail dirs, descriptor nodes, allocation counters, and close counters.
- `struct fdnode`: descriptor slot containing file pointer, flags, reservation state, cache links, and allocation metadata.
- `struct fdcache`: per-thread cache entries that can temporarily lend or hold `struct file` references.
- `fildesc_ops`: device ops for `/dev/fd`.
- `badfileops`: file operation table that returns errors for invalid/revoked/uninitialized file objects.

## Descriptor Lookup and Cache Flow

- `holdfp_fdp()` and `holdfp_fdp_locked()` acquire a referenced file pointer from an arbitrary descriptor table.
- `_holdfp_cache()` first searches the current thread’s fd cache; on miss it locks the descriptor table, holds the file, and may install a cache entry.
- `dropfp()` tries to return a borrowed cache reference; if it cannot, it drops the file normally.
- `fexitcache()` clears all cached descriptors for a thread, used before descriptor table destruction/replacement.
- `fclearcache()` removes descriptor cache entries when a descriptor is cleared or replaced.

## Descriptor Allocation

- `fdgrow_locked()` grows the descriptor table to `2^n - 1` size, preserving the allocation tree layout.
- `right_subtree_size()`, `right_ancestor()`, and `left_ancestor()` implement navigation for the in-place allocation tree.
- `fdreserve_locked()` increments/decrements allocation counts up the tree.
- `fdalloc_locked()` enforces `RLIMIT_NOFILE`, `maxfilesperproc`, `minfilesperproc`, and per-user limits, then finds/reserves a free descriptor.
- `fdalloc()` wraps allocation with descriptor table locking.
- `fdavail()` tests whether a process has enough free descriptors.

## Syscall and Helper Entry Points

- `sys_getdtablesize()` returns the effective descriptor-table size cap.
- `sys_dup2()`, `sys_dup()`, and `kern_dup()` implement descriptor duplication, including fixed/variable allocation and `CLOEXEC`/`CLOFORK` variants.
- `sys_fcntl()` and `kern_fcntl()` implement descriptor flags, file status flags, owner ioctls, advisory record locks, `F_GETPATH`, and multiple dup commands.
- `sys_close()`, `kern_close()`, `sys_closefrom()`, `kern_closefrom()` remove descriptor table entries and close underlying files.
- `sys_shutdown()` / `kern_shutdown()` dispatch `fo_shutdown()`.
- `sys_fstat()` / `kern_fstat()` dispatch `fo_stat()`.
- `sys_fpathconf()` dispatches pathconf for vnode/fifo and pipe/socket cases.
- `sys_flock()` implements BSD whole-file advisory locks.

## File Object Lifetime

- `falloc()` creates a `struct file`, initializes `f_count`, `f_ops`, credentials, kqueue list, global file-list insertion, and optionally reserves a descriptor.
- `fsetfd_locked()` installs or clears a reserved descriptor.
- `funsetfd_locked()` removes a file pointer from a descriptor, clears cache entries, updates allocation counters, and returns the file reference previously owned by the descriptor table.
- `fhold()` increments `f_count`.
- `fdrop()` safely performs the last-reference transition by removing the file from the global file list under the list spinlock before calling `fo_close()` and `ffree()`.
- `ffree()` releases credentials, namecache handle, and memory.
- `fsetcred()` synchronizes `uidinfo` open-file counts, including per-CPU batching.

## Descriptor Table Lifecycle

- `fdinit_bootstrap()` initializes proc0’s file descriptor table.
- `fdinit()` creates a new descriptor table inheriting cwd/root/jail dirs.
- `fdshare()` increments table refcount for shared descriptor tables.
- `fdcopy()` clones descriptor tables across fork-like operations, dropping reserved slots and not copying kqueue descriptors or `UF_FOCLOSE` descriptors.
- `fdfree()` releases descriptor tables, closes files, handles POSIX lock leader structures, waits for soft references from process scans, and releases directory/namecache references.
- `filedesc_to_leader_alloc()` manages process-leader lock-cleanup topology for shared descriptor tables.

## Revocation

- `fdrevoke()` allocates a replacement dummy file, marks matching file pointers `FREVOKED` via `allfiles_scan_exclusive()`, then scans processes to replace matching descriptors and close old files.
- `fdrevoke_check_callback()` filters by prison and file data/type.
- `fdrevoke_proc_callback()` handles process descriptor replacement and controlling-terminal cleanup.

## `/dev/fd` Handling

- `fildesc_drvinit()` creates `fd/0` through `fd/63`, plus `stdin`, `stdout`, and `stderr`.
- `fdopen()` implements `/dev/fd/N` open semantics:
  - Looks up the source descriptor.
  - Rejects incompatible access modes.
  - For vnode-backed descriptors, creates a new file pointer so seek offset is not shared.
  - For non-vnode descriptors, shares the existing file pointer.
  - Handles revoked descriptors by substituting a dummy file.

## Exec and Setuid Safety

- `setugidsafety()` closes unsafe procfs descriptors in fd 0..2 for setuid/setgid exec safety.
- `fdcloseexec()` closes `UF_EXCLOSE` descriptors and clears `UF_FOCLOSE` across exec.
- `fdcheckstd()` opens `/dev/null` for missing standard descriptors 0, 1, and 2.

## Sysctl Surface

- `kern.file` returns `struct kinfo_file` snapshots through `sysctl_kern_file()`.
- `kern.minfilesperproc`, `kern.maxfilesperproc`, `kern.maxfilesperuser`, `kern.maxfiles`, `kern.maxfilesrootres`, `kern.openfiles`.

## Filesystem/Storage Relevance

This file is directly VFS-critical. Every open vnode, device vnode, pipe, socket, and kqueue descriptor flows through this layer. Close paths invoke vnode advisory lock cleanup and file operations; `/dev/fd` can reopen vnode-backed descriptors; revocation supports forced invalidation of descriptors referencing revoked vnodes/devices.

## Research Notes

- Descriptor cache correctness depends on careful interaction between `fclearcache()`, borrowed references, and descriptor-table spinlocks.
- The allocation tree in `fd_files[].allocated` avoids linear scans for large descriptor tables.
- `closef()` implements POSIX record-lock behavior: a close by a process can release all process-owned POSIX locks on a vnode.
- `fdrop()` avoids last-reference races with global file-list scanners by removing the file from the list while holding the list spinlock.
- Several functions are marked not fully MPSAFE in comments, especially paths that scan descriptor tables while operations can block.
