# File Research: sources/teaching/minix/minix/servers/vfs/dmap.h

Header defining the VFS device-driver map entry.

`struct dmap` fields:
- `dmap_driver`: driver endpoint.
- `dmap_label`: driver label.
- `dmap_sel_busy`, `dmap_sel_filp`: select-related state.
- `dmap_servicing`: worker thread currently synchronously servicing this driver.
- `dmap_lock`: per-entry mutex.
- `dmap_recovering`: block-driver recovery guard.
- `dmap_seen_tty`: optimization/control flag for controlling TTY checks.

The header declares the global `dmap[]` table.
