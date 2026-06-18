# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/user.h

## Role

Defines process user-area data structures for kernel/kmem consumers and a reduced compatibility `struct user` for userland ptrace-style register access.

## Key Interfaces

- `struct exdata` records executable vnode, text/data/bss/library sizes, machine/magic values, file offsets, memory origins, and entry address.
- Kernel/kmem section defines file descriptor generation type `uf_entry_gen_t`.
- `uf_entry_t` is a per-file-descriptor entry with fd lock, file pointer, poll info, refcount, allocation/busy flags, close/set wait CVs, port association, assignment generation, and cache-line padding.
- `uf_rlist_t` tracks retired file lists.
- `uf_info_t` is per-process file descriptor table state with lock, bad-fd policy, table size, current fd list, and retired lists.
- `UF_ENTER`/`UF_EXIT` implement safe fd-entry locking against concurrent file-list growth.
- Defines `PSARGSZ`, `MAXCOMLEN`, `k_sysset_t`, and architecture-dependent `__KERN_NAUXV_IMPL`.
- Kernel `user_t` stores exec metadata, aux vector, start time/ticks, command/args, argv/envp/commpage pointers, cwd/root/current dir, memory/accounting/proc signal masks/handlers, saved rlimits, and open file info.
- Userland fallback `user_t` exposes saved registers, register pointer, ps args, signal dispositions, trap code, and fault address.

## Risk Notes

File descriptor locking rules are explicitly documented and subtle. `UF_ENTER` protects against `fi_list` replacement during `flist_grow()`. Any consumer bypassing these rules risks use-after-free or locking stale fd entries.
