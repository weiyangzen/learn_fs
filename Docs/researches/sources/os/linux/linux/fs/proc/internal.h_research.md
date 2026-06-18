# File Research: sources/os/linux/linux/fs/proc/internal.h

## Scope

This internal header defines the core procfs private structures, helper accessors, procfs cross-file prototypes, process map private state, and compile-time feature stubs used by the `fs/proc` implementation.

## Public And Internal APIs Covered

- Core structures: `struct proc_dir_entry`, `struct proc_inode`, `struct pde_opener`, `struct proc_maps_locking_ctx`, and `struct proc_maps_private`.
- Accessors: `PROC_I()`, `PDE()`, `proc_pid()`, `get_proc_task()`, `pde_get()`, `is_empty_pde()`, `pde_force_lookup()`, and `proc_splice_unmountable()`.
- Mapcount helpers: `folio_precise_page_mapcount()` under `CONFIG_PAGE_MAPCOUNT`, and `folio_average_page_mapcount()`.
- Declarations for proc root, generic proc directory handling, pid handling, net handling, namespace handling, sysctl handling, tty init, task memory reporting, pagemap, and process maps operations.

## Control Flow And Behavior

- `struct proc_dir_entry` is the in-memory proc tree node. It stores lifetime counters, unload synchronization, file or directory operation pointers, seq/single show callbacks, write callback, data pointer, inode metadata, rb-tree directory links, name storage, mode, and flags.
- `struct proc_inode` embeds `struct inode` and adds proc-specific associations: PID, fd number, operation union, PDE pointer, sysctl header and entry, sibling hlist link, and namespace operations.
- `SIZEOF_PDE` rounds PDE allocation size to one of several cache-friendly buckets and reserves inline name space.
- Permanent PDE helpers distinguish built-in entries that do not need module unload protection from dynamic/module entries.
- Mapcount helpers centralize precise vs approximate per-page mapping counts for `/proc/kpagecount`, `smaps`, and `numa_maps`.
- `proc_maps_private` carries the inode, pinned task, VMA iterator, last position, locking context, and optional NUMA task mempolicy for `/proc/<pid>/maps`-style readers.
- `proc_splice_unmountable()` marks ephemeral proc dentries as non-mountable before splicing aliases.

## Dependencies

- Pulls in procfs, namespace, refcount, spinlock, binfmt, coredump, task, and MM headers.
- Provides shared contracts consumed by nearly every file in this group, especially `inode.c`, `root.c`, `proc_sysctl.c`, `proc_net.c`, `namespaces.c`, and `task_mmu.c`.

## Risks And Invariants

- `proc_dir_entry` lifetime is split between `refcnt`, `in_use`, `nreg`, and VFS inode references; callers must use the intended mechanism for their context.
- `PROC_I()` assumes all procfs inodes were allocated with embedded `struct proc_inode`.
- Mapcount helpers document that precise mapcount is for statistics and debugging only; new code should avoid depending on it for semantics.
- `pde_force_lookup()` is important for namespace-sensitive entries, especially `/proc/net`, where setns can change visible contents under an existing dentry name.
