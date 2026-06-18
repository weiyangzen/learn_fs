# File Research: sources/os/linux/linux-stable/fs/proc/proc_net.c

Implements network namespace-aware proc entries and `/proc/<pid>/net`.

Key points:
- `PDE_NET()` obtains the namespace from a proc net directory PDE.
- `seq_open_net()` pins the net namespace and opens seq private state; release drops net refs.
- Provides exported helpers:
  - `proc_create_net_data()`
  - `proc_create_net_data_write()`
  - `proc_create_net_single()`
  - `proc_create_net_single_write()`
- Net proc entries force lookup because `/proc/net` can change across `setns(CLONE_NEWNET)`.
- `/proc/<pid>/net` lookup/readdir uses the target task's `nsproxy->net_ns`.
- Per-net init allocates anchor PDE `net->proc_net`, creates `stat`, assigns root uid/gid in the net user namespace, and marks lookup forced.
- Global init creates `/proc/net -> self/net` symlink and registers pernet operations.

Dependencies/contracts:
- Uses net namespace lifetime tracking, seq_file private state, and task namespace access.
- Anchor PDE for `/proc/<pid>/net` is not normally instantiated as its own inode.
