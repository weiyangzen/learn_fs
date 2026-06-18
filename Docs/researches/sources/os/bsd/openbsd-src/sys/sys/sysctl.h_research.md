# File Research: sources/os/bsd/openbsd-src/sys/sys/sysctl.h

Sysctl hierarchy ABI, exported kernel data structs, and kernel sysctl helper declarations.

This header defines the integer-MIB sysctl namespace: top-level `CTL_*` nodes, type descriptors, name tables, and a large `CTL_KERN` subtree with process, vnode, file, mbuf, pool, SysV IPC, watchdog, timecounter, audio/video, CPU, PF, timeout, and autoconf entries. It also defines `KERN_PROC` filters, SysV IPC info selectors, process-argument selectors, media subtrees, witness controls, interrupt counters, watchdog controls, timecounter controls, clock interrupt stats, `CTL_HW` hardware identifiers, battery controls, and `CTL_DEBUG` layout.

The file defines public reporting structs `kinfo_proc`, `kinfo_vmentry`, and `kinfo_file`, including stable layout comments, process/thread identity, credentials, signal state, VM metrics, rusage, pledge, vnode/file/socket/pipe/kqueue fields, and filesystem mount/name data. Kernel/libkvm builds get `FILL_KPROC()` helpers for populating `kinfo_proc`.

Kernel builds expose the sysctl implementation ABI: `sysctlfn`, `sysctl_lock`, user-buffer locking, typed integer/string/struct/quad helpers, bounded integer helpers, process/file/route/socket queue dump helpers, and subsystem dispatchers for kern/hw/debug/net/cpu/vfs/SysV IPC/watchdog plus network submodules. Userland gets the `sysctl()` prototype.

Filesystem/storage relevance: very high. `CTL_VFS`, vnode/file counters, `KERN_FILE`, `KERN_NCHSTATS`, `KERN_NUMVNODES`, buffer-cache percentage, hardware disk names/stats/count, sensors, and process cwd/vmmap data all expose filesystem and storage state to userland.
