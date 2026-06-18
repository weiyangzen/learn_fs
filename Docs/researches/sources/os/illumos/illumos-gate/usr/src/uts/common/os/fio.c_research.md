# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/fio.c

## Purpose

`fio.c` implements kernel file descriptor and `file_t` management: descriptor allocation, descriptor-table growth, get/release reference tracking, close/replacement, fork/exec/exit descriptor handling, file object allocation/freeing, fd flags, `*at()` start-vnode helpers, poll/event-port descriptor associations, and zone-change checks.

It is foundational VFS/process glue and is used heavily by exec, exit, open/close/fcntl, poll, event ports, and auditing.

## Descriptor Allocation Model

The file descriptor table is represented as an infix binary tree embedded in an array of `uf_entry_t`. Each entry’s `uf_alloc` tracks allocation counts for descriptor-search subtrees. The large comment at the top derives the math for `fd_find()`, `fd_reserve()`, `flist_minsize()`, and `flist_nalloc()`.

- `fd_find()` finds the smallest free fd >= `minfd` in `O(log n)`.
- `fd_reserve()` increments or decrements allocation counts along left ancestors and toggles `uf_busy`.
- `flist_minsize()` finds the minimum table size needed for fork copying.
- `flist_nalloc()` counts currently allocated descriptors.
- `flist_grow()` expands `fi_list` to a `2^n - 1` size, copies entries, uses memory barriers to publish `fi_list` before `fi_nfiles`, wakes waiters on old condition variables, and retires old tables on `fi_rlist` for later exit cleanup.

The grow path is concurrency-heavy: it locks old entries and visible new entries to preserve `UF_ENTER()` semantics while the array pointer changes.

## Active File Descriptor Tracking

Each thread has `t_activefd`, used to detect and interrupt syscalls using an fd that another LWP is closing.

- `set_active_fd()` records fd activity and grows the per-thread active-fd buffer if needed.
- `clear_active_fd()` removes a recorded active fd.
- `is_active_fd()` checks another thread under its active-fd lock.
- `clear_stale_fd()` runs from `post_syscall()` to clear stale state.
- `free_afd()` frees or resets active-fd buffers.

This supports `closeandsetf()` invalidating concurrent users without stopping every LWP.

## File Lookup, Release, and Close

`getf_gen()` validates fd range, reserves active-fd space, locks the descriptor entry, increments `uf_refcnt`, optionally returns generation, records the active fd, and returns the `file_t`. `getf()` is the simple wrapper.

`releasef()` decrements `uf_refcnt`, clears the active fd, and wakes close waiters when the count reaches zero. `areleasef()` performs the same reference drop against an explicitly supplied `uf_info_t`.

`closeandsetf()` is the core close/replace path. It handles table growth for installing a new file, waits for reserved-but-not-yet-filled slots, rejects the process poison fd, removes the old `uf_file`, wakes other LWPs using the fd by marking active-fd stale state, waits for `uf_refcnt` to drain, cleans poll cache and event port associations, calls `closef()`, and finally installs `newfp` with `setf()`.

`closef()` decrements the `file_t` reference count, calls `VOP_CLOSE()` with the current count/flags/offset, removes OFD locks on the last reference, invokes a DTrace close barrier if installed, releases the vnode, frees audit and credential state, and returns the `file_t` to `file_cache`.

## Allocation and File Object Lifecycle

- `ufalloc_file()` combines descriptor allocation and optional immediate `file_t` installation, enforcing `RLIMIT_NOFILE`.
- `ufalloc()` allocates a reserved descriptor with no file pointer.
- `ufcanalloc()` estimates whether a process can allocate a future number of fds and triggers rctl action on likely failure.
- `falloc()` allocates a `file_t`, initializes flags, offset, vnode, credential hold, and audit state, optionally reserving an fd first. It returns the `file_t` locked.
- `unfalloc()` undoes a failed allocation path.
- `finit()` creates the `file_cache` kmem cache.

`setf()` installs or clears a descriptor slot, updates descriptor generation when installing a real file, broadcasts waiters, and audits the fd assignment.

## Fork, Exec, and Exit Descriptor Handling

`flist_fork()` copies the parent descriptor table into the child when fork has already reduced parent concurrency. It preserves files and flags except descriptors marked `FD_CLOFORK`, which are omitted from the child and unreserved in allocation accounting.

`fcntl_add()` increments or decrements `file_t` reference counts across fork success/failure.

`close_exec()` is called by exec. It closes descriptors marked `FD_CLOEXEC` and writable self-open `/proc` descriptors, clears poll/event-port state, and closes the underlying file. It also clears `FD_CLOFORK` on surviving descriptors, deliberately diverging from early POSIX 2024 wording to avoid surprising post-exec descriptor disappearance. Finally it resets the poison fd state.

`closeall()` is the exit path: because exit is single-threaded, it iterates without locking, closes every open file, removes event-port associations, frees `fi_list`, and frees retired descriptor lists.

## Descriptor Flags and Poison FD

`f_getfl()` returns file status flags plus BSD-compatible socket `FASYNC` state. `f_getfd_error()` returns fd flags and forces `FD_CLOEXEC` for writable self-open `/proc` files. `f_getfd()` is the getf-era wrapper.

`f_setfd_int()` updates `FD_CLOEXEC`/`FD_CLOFORK`, either replacing or OR-ing flags. `f_setfd_error()` and `f_setfd_or()` expose that behavior.

`f_badfd()` allocates a “poison” bad fd for ILP32 compatibility cases. The selected fd cannot be reused normally; attempts to use it can trigger configured signal action. It is restricted to fd 3 through 255 and only one poison fd may exist per process.

## Vnode Helpers and Zone Checks

`fassign()` allocates a descriptor and `file_t`, opens a vnode with `VOP_OPEN()`, installs the vnode into the file, and publishes the fd.

`fgetstartvp()` is used by `*at()` syscalls and descriptor exec. It returns a held starting vnode for `(fd, path)` unless `AT_FDCWD` or an absolute path means normal cwd/root lookup should apply.

`fsetattrat()` implements common `fchownat()`/`fchmodat()` setup: obtains start vnode, optionally audits, resolves path with follow/no-follow semantics, rejects chmod of symlinks, rejects readonly filesystems, then calls `VOP_SETATTR()`.

`fisopen()` checks whether the current process has a vnode open. `files_can_change_zones()` returns false if any open file’s vnode disallows zone changes.

## Poll and Event Port Associations

The file tracks fd-to-poll cache membership with `fpollinfo_t` lists:

- `addfpollinfo()` records current thread polling an fd.
- `delfpollinfo()` removes it.
- Debug-only `checkfpollinfo()` and `infpollinfo()` assert/inspect membership.

Event port associations are tracked with `portfd_t` lists:

- `addfd_port()` links a port fd entry into a descriptor.
- `delfd_port()` unlinks it.
- `port_close_fd()` closes all event port associations for a descriptor after the descriptor slot has been cleared.

## External Interactions

This file is coupled to VFS (`VOP_CLOSE`, `VOP_OPEN`, `VOP_SETATTR`, vnode references), process limits/resource controls, `/proc` self-open semantics, poll cache cleanup, event ports, DTrace close barriers, audit hooks, credentials, fork/exec/exit paths, and zone migration policy.

## Research Notes

The most important invariants are descriptor-table publication ordering in `flist_grow()`, `uf_refcnt` draining before fd reuse, active-fd stale signaling for concurrent close, correct accounting through `fd_reserve()`, and fork/exec special handling for `FD_CLOFORK`, `FD_CLOEXEC`, and writable self-open `/proc` descriptors.
