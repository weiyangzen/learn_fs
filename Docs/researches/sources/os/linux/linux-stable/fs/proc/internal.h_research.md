# File Research: sources/os/linux/linux-stable/fs/proc/internal.h

Internal procfs header shared by proc implementation files.

Key points:
- Defines `struct proc_dir_entry`, including reference counts, openers list, proc ops, seq/single callbacks, rb-tree child directory state, ownership, mode, and inline name storage.
- Defines PDE sizing macros and helpers for permanent entries and optional `proc_ops` capabilities.
- Defines `struct proc_inode`, embedding VFS inode plus PID, PDE, sysctl, namespace, and file-descriptor metadata.
- Provides `PROC_I()`, `PDE()`, `proc_pid()`, and `get_proc_task()` helpers.
- Declares proc root, PID, generic directory, inode, namespace, net, sysctl, tty, self, thread-self, and task memory interfaces.
- Provides mapcount helpers used by page, smaps, kpagecount, and numa reporting:
  - precise page mapcount when `CONFIG_PAGE_MAPCOUNT`
  - averaged folio mapcount otherwise
- Defines `proc_maps_private` and `proc_maps_locking_ctx` shared by MMU/NOMMU task map reporting.

Dependencies/contracts:
- This header is the local ABI between procfs implementation units.
- The PDE lifetime fields are tightly coupled to `inode.c`.
- The sysctl inode sibling list is coupled to `proc_sysctl.c`.
