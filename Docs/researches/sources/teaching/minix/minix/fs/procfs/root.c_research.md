# File Research: sources/teaching/minix/minix/fs/procfs/root.c

`root.c` defines the static files in the ProcFS root and their generator functions. `root_files` includes `hz`, `uptime`, `loadavg`, `kinfo`, `meminfo`, `dmap`, `ipcvecs`, and `mounts`, plus i386-only `pci` and `cpuinfo`.

Generators are lightweight snapshots of system state. `root_hz` prints clock frequency, `root_uptime` prints uptime in seconds with two decimals, `root_loadavg` formats 1/5/15-minute load averages from `procfs_getloadavg`, `root_kinfo` prints process/task counts, and `root_meminfo` prints VM page size and memory totals/free/largest/cached.

On i386, `root_pci` initializes PCI once and prints slot/class/revision/vendor/device/subsystem/name records. `root_dmap` dumps assigned major-device mappings from VFS. `root_ipcvecs` prints kernel IPC vector entrypoints only when kernel info says they are exported. `root_mounts` uses `getvfsstat` and prints mounted filesystem source, target, type, and read-only/read-write status.
