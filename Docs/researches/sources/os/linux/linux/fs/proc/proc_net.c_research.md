# File Research: sources/os/linux/linux/fs/proc/proc_net.c

## Scope

This file implements network-namespace-aware proc helpers and `/proc/<pid>/net` directory behavior.

## Public And Internal APIs Covered

- Net seq helpers: `proc_create_net_data()`, `proc_create_net_data_write()`.
- Net single helpers: `proc_create_net_single()`, `proc_create_net_single_write()`.
- BPF iterator hooks: `bpf_iter_init_seq_net()`, `bpf_iter_fini_seq_net()`.
- `/proc/<pid>/net` inode and file ops: `proc_net_inode_operations`, `proc_net_operations`.
- Net namespace lifecycle: `proc_net_ns_init()`, `proc_net_ns_exit()`, `proc_net_init()`.

## Control Flow And Behavior

- Per-entry net namespace is derived from the parent PDE data through `PDE_NET()` and pinned with `maybe_get_net()`.
- `seq_open_net()` checks write permission against PDE write support, pins the namespace, allocates seq private state, and stores/tracks `struct net` under `CONFIG_NET_NS`.
- Release paths drop the namespace reference and release seq private state.
- `proc_create_net_data*()` and `proc_create_net_single*()` allocate PDEs, force lookup revalidation, attach net-aware proc ops and seq/single callbacks, and register entries.
- `get_proc_task_net()` finds the target task namespace under RCU/task lock, pins it, and enforces `subset=pid` visibility by requiring mounter `CAP_NET_ADMIN` in the network namespace userns.
- `/proc/<pid>/net` lookup, getattr, and readdir delegate into the target net namespace's `proc_net` PDE tree.
- Each network namespace gets a synthetic `net` PDE anchor and `stat` subdirectory. The root `/proc/net` is a symlink to `self/net`.

## Dependencies

- Depends on network namespace lifetime APIs, pernet subsystem registration, proc generic directory helpers, seq_file private allocation, BPF iterator net private state, and security capability checks.

## Risks And Invariants

- `/proc/<pid>/net` is namespace-sensitive; `pde_force_lookup()` prevents stale dentry reuse across `setns(CLONE_NEWNET)` changes.
- Namespace references must be dropped through matching tracked or untracked put helpers.
- The synthetic per-net `net` anchor is not normally instantiated as an inode, so initialization manually fills only the fields needed for directory lookup.
